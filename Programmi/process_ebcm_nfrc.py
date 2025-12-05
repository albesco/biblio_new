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
    
    ##############################################################################################################
    # API Key settings
    # API_KEY = "c81e40b973484fb83db5c697eadc3bea" # Chiave API Cast
    # API_KEY = "18acfcf2e6f1ef665eec335c2fc40fcc" # Chiave API Forlano
    # API_KEY = "10f7de16ece6898e37b7f9c6d6a68eb7" # Chiave API Caputo
    # API_KEY = "a4be5d6403465914a622246057f086e0" # Chiave API Scocco 1
    # API_KEY = "d1dd3948f277cd381a11337c51d72f67" # Chiave API Scocco 2

    # To be used with revolver of API keys, to avoid exceeding the maximum number of requests per minute/hour/day

    API_KEY_PAUSE_TIME      =       20 # Time in seconds to pause between the switch to the next api key use
    API_KEY_ROLL_PAUSE_TIME = 60*60*0.5 # Time in seconds to pause between the switch to the first api key after a complete loop of all the available keys

    MAX_KEY_LOOPS  = 30            # Maximum number of loops to check the API keys
    CITATION_PAUSE_TIME     =   2.5 # Time in seconds to pause between two subsequent queries on citations for the same article, to avoid exceeding the maximum number of requests per minute/hour/day
    PAUSE_TIME_BETWEEN_QUERIES = 0.2 # Time in seconds to pause between two subsequent queries when retrieving details for citing articles
    
    
    API_KEYS = [ 
             "c81e40b973484fb83db5c697eadc3bea",  # Chiave API Cast
             "a4be5d6403465914a622246057f086e0",  # Chiave API Scocco 1
             "10f7de16ece6898e37b7f9c6d6a68eb7",  # Chiave API Caputo
             "18acfcf2e6f1ef665eec335c2fc40fcc",  # Chiave API Forlano 
             "2e47c27c5a96dc921842c11144168480",  # Chiave API Scocco 3
             "d1dd3948f277cd381a11337c51d72f67" ] # Chiave API Scocco 2

    ##############################################################################################################
    # Scopus API keys settings

    cont_key       = -1      # Counter for the current API key to be used. Starts from -1, so the first key will be the 0th in the list
    cont_key_loops = 0       # Counter for the number of loops to check the API keys

    api_key_revolver = {
        "api_key"           : "",
        "API_KEYS"          : API_KEYS,
        "cont_key"          : cont_key,
        "cont_key_loops"    : cont_key_loops,
        "MAX_KEY_LOOPS"     : MAX_KEY_LOOPS,
        "log_file_path"     : log_file_path,
        "api_key_pause_time"     : API_KEY_PAUSE_TIME,
        "api_key_roll_pause_time": API_KEY_ROLL_PAUSE_TIME,
        "citation_pause_time"    : CITATION_PAUSE_TIME
    }

    functions_revolver.log_file_setup(log_file_path)
    
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"--- Inizio elaborazione NRFC: {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        f.write(f"Lettura EIDs da: {input_csv_file_path}\n")
        f.write(f"Output scritto su: {output_csv_file_path}\n")

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
                    if year == -1:
                        print(f"    ({j+1}/{len(list_citing_eids)}) EID citante {citing_eid}: Da API risulta NOT FOUND, quindi verrà eliminato dalla lista.")
                        continue # Salta questo articolo citante dalla lista   

                    print(f"    ({j+1}/{len(list_citing_eids)}) EID citante {citing_eid}: Anno: {year}, Referenze: {ref_count} (da API).")

                    list_citing_years.append(year)
                    list_ref_counts.append(ref_count)
                    time.sleep(PAUSE_TIME_BETWEEN_QUERIES)

            # Calcola il nuovo valore di num_ref_in_citing
            num_ref_in_citing = 0.0
            for ref_count in list_ref_counts:
                if ref_count > 0:
                    num_ref_in_citing += (1.0 / ref_count)

            # Conteggio degli articoli citanti trovati
            num_citing_articles = len(list_citing_years)

            # Scrivi il record nel file di output
            output_record = article_to_process.copy()
            output_record['num_cit'] = num_citing_articles
            output_record['citing_years'] = list_citing_years
            output_record['list_citing'] = list_citing_eids
            output_record['list_num_ref_of_citing'] = list_ref_counts
            # Aggiorna il campo 'num_ref_in_citing' con il valore calcolato
            output_record['num_ref_in_citing'] = num_ref_in_citing

            writer.writerow(output_record)
            outfile.flush() # Forza la scrittura immediata su disco

            print(f"[{i+1}/{total_articles}] Elaborazione EID: {article_eid} completata e salvato su {output_csv_file_name}\n.")
            print(f" -> N.articoli citanti: {num_citing_articles}\n")
            print(f" -> Lista anno articoli citanti: {list_citing_years}\n")
            print(f" -> Lista EID articoli citanti: {list_citing_eids}\n")
            print(f" -> Lista numeri di referenze degli articoli citanti: {list_ref_counts}\n")
            print(f" -> Somma frazioni 1/num_referenze per articoli citanti: {num_ref_in_citing}\n")
            print(f" -> N.citazioni saltate perché non trovate: {len(list_citing_eids) - len(list_ref_counts)}\n")

    print("\nElaborazione completata.")

if __name__ == "__main__":
    process_ebcm_to_nrfc()