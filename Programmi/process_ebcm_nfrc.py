import os
import csv
import time
import sys
import platform
import functions_revolver

def get_data_dir_path(reference_name):
    """Determina il percorso della directory dei dati basandosi sul sistema operativo e sul nome host."""
    base_dir_path = ""
    if platform.system() == "Windows":
        hostname = platform.node()
        if hostname == 'DESKTOP-K6PVP1F':
            base_dir_path = r"F:\biblio_new\Dati"
        elif hostname == 'Grifone':
            base_dir_path = r"F:\OneDrive - Università Politecnica delle Marche\Attivita\UnivPM\20250327_Bibliometry\Dati"
        else:
            print(f"AVVISO: Computer non riconosciuto: '{hostname}'. Utilizzo un percorso di default per Windows.")
            base_dir_path = os.path.join(os.path.expanduser("~"), "Documents", "biblio_new", "Dati")
    else:
        print(f"AVVISO: Il sistema operativo '{platform.system()}' non è Windows. Utilizzo un percorso di default.")
        base_dir_path = os.path.join(os.path.expanduser("~"), "biblio_new", "Dati")

    return os.path.join(base_dir_path, reference_name)

def process_ebcm_to_nrfc():
    REFERENCE_NAME = "EBMC_lista_citing"
    input_csv_file_name = REFERENCE_NAME + ".csv"
    output_csv_file_name = REFERENCE_NAME + "_NRFC.csv"
    log_file_name = REFERENCE_NAME + "_nrfc_script_log.txt"

    data_dir_path = get_data_dir_path(REFERENCE_NAME)
    input_csv_file_path = os.path.join(data_dir_path, input_csv_file_name)
    output_csv_file_path = os.path.join(data_dir_path, output_csv_file_name)
    log_file_path = os.path.join(data_dir_path, log_file_name)

    # API_KEY_VALUE = "c81e40b973484fb83db5c697eadc3bea"
    API_KEY_VALUE = "18acfcf2e6f1ef665eec335c2fc40fcc"
    PAUSE_TIME_BETWEEN_QUERIES = 1.0

    api_key_revolver = {
        "api_key": API_KEY_VALUE,
        "API_KEYS": [API_KEY_VALUE],
        "cont_key": 0,
        "cont_key_loops": 0,
        "MAX_KEY_LOOPS": 5,
        "log_file_path": log_file_path,
        "api_key_pause_time": 1,
        "api_key_roll_pause_time": 60,
        "citation_pause_time": PAUSE_TIME_BETWEEN_QUERIES
    }

    functions_revolver.log_file_setup(log_file_path)
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"--- Inizio elaborazione NRFC: {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        f.write(f"Lettura EIDs da: {input_csv_file_path}\n")
        f.write(f"Output scritto su: {output_csv_file_path}\n")
        f.write(f"Utilizzo API Key: 'API_KEY_VALUE' ({API_KEY_VALUE})\n")

    # Carica il file di input in memoria per una ricerca efficiente
    print(f"Caricamento dati da {input_csv_file_path} per ottimizzazione...")
    input_articles_by_eid = {}
    input_articles_data = functions_revolver.load_CSV_articles(input_csv_file_path)
    if not input_articles_data:
        print("File di input non trovato o vuoto. Uscita.")
        return
        
    for article in input_articles_data:
        if 'article_eid' in article:
            input_articles_by_eid[article['article_eid']] = article
    print(f"Caricati {len(input_articles_by_eid)} articoli dal file di input.")

    # Carica gli EID già processati dal file di output
    processed_eids = set()
    if os.path.exists(output_csv_file_path):
        print(f"Caricamento EID già processati da {output_csv_file_path}...")
        output_data = functions_revolver.load_CSV_articles(output_csv_file_path)
        for row in output_data:
            if 'article_eid' in row:
                processed_eids.add(row['article_eid'])
        print(f"Trovati {len(processed_eids)} record già elaborati. Verranno saltati.")

    output_file_exists = os.path.exists(output_csv_file_path)
    
    with open(output_csv_file_path, 'a', encoding='utf-8', newline='') as outfile:
        # Le colonne del file di output
        fieldnames = list(input_articles_data[0].keys()) + ['list_citing', 'list_num_ref_of_citing']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='|')

        if not output_file_exists or os.stat(output_csv_file_path).st_size == 0:
            writer.writeheader()
            writer.flush() # Forza la scrittura immediata su disco

        total_articles = len(input_articles_data)
        for i, article_to_process in enumerate(input_articles_data):
            article_eid = article_to_process.get("article_eid")

            if not article_eid:
                print(f"Record {i+1} saltato: 'article_eid' mancante.")
                continue

            # Salta i record già presenti nel file di output
            if article_eid in processed_eids:
                print(f"[{i+1}/{total_articles}] EID: {article_eid} già processato. Saltato.")
                continue

            print(f"[{i+1}/{total_articles}] Elaborazione EID: {article_eid}...")

            # a) Trova la lista L degli articoli citanti (EIDs)
            print(" -> Recupero articoli citanti...", end="", flush=True)
            list_citing_eids = functions_revolver.get_citing_articles_EID( article_eid , api_key_revolver )
            print(f" Trovati {len(list_citing_eids)} articoli.")

            # Conteggio degli articoli citanti trovati
            num_citing_articles = len(list_citing_eids)


            # b) Trova la lista LRC con il numero di referenze per ogni articolo in L
            # e la lista degli anni di pubblicazione
            list_ref_counts = []
            list_citing_years = []
            if list_citing_eids:
                print(f" -> Recupero dettagli (anno e referenze) per i {len(list_citing_eids)} articoli citanti...")
                for j, citing_eid in enumerate(list_citing_eids):
                    # Usa la nuova funzione per ottenere anno e referenze con una sola chiamata
                    print(f"    ({j+1}/{len(list_citing_eids)}) EID citante {citing_eid}: Query API...")
                    year, ref_count = functions_revolver.get_details_from_eid(citing_eid, api_key_revolver)
                    print(f"    ({j+1}/{len(list_citing_eids)}) EID citante {citing_eid}: Anno: {year}, Referenze: {ref_count} (da API).")

                    list_citing_years.append(year)
                    list_ref_counts.append(ref_count)
                    time.sleep(PAUSE_TIME_BETWEEN_QUERIES)

            # Scrivi il record nel file di output
            output_record = article_to_process.copy()
            output_record['num_cit'] = num_citing_articles
            output_record['citing_years'] = list_citing_years
            output_record['list_citing'] = list_citing_eids
            output_record['list_num_ref_of_citing'] = list_ref_counts
            writer.writerow(output_record)
            outfile.flush() # Forza la scrittura immediata su disco
            print(f" -> Record per EID {article_eid} salvato su {output_csv_file_name}.\n")

    print("\nElaborazione completata.")

if __name__ == "__main__":
    process_ebcm_to_nrfc()