import os
import csv
import time
import sys
import platform # Usato per platform.node() come nell'originale main_revolver.py

FIRST_ARTICLE_TO_PROCESS = 16128
# Aggiunge la directory contenente functions_revolver.py al Python path
# Questo assume che il nuovo script si trovi nella stessa directory di functions_revolver.py
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import functions_revolver

def get_data_dir_path(reference_name):
    """Determina il percorso della directory dei dati basandosi sul sistema operativo e sul nome host,
    rispecchiando la logica di main_revolver.py."""
    base_dir_path = ""
    if platform.system() == "Windows":
        hostname = platform.node()
        if hostname == 'DESKTOP-K6PVP1F':  # Sostituisci con il nome reale del PC "Calypso"
            base_dir_path = r"F:\biblio_new\Dati"
        elif hostname == 'Grifone': # Sostituisci con il nome reale del PC "Alberto"
            base_dir_path = r"F:\OneDrive - Università Politecnica delle Marche\Attivita\UnivPM\20250327_Bibliometry\Dati"
        else:
            print(f"AVVISO: Computer non riconosciuto: '{hostname}'. Utilizzo un percorso di default per Windows.")
            base_dir_path = os.path.join(os.path.expanduser("~"), "Documents", "biblio_new", "Dati")
    else:
        print(f"AVVISO: Il sistema operativo '{platform.system()}' non è Windows. Utilizzo un percorso di default.")
        base_dir_path = os.path.join(os.path.expanduser("~"), "biblio_new", "Dati")

    return os.path.join(base_dir_path, reference_name)

def process_ebmc_authors():
    REFERENCE_NAME = "EBMC_0"
    input_csv_file_name = REFERENCE_NAME + ".csv"
    output_csv_file_name = REFERENCE_NAME + "_Authors.csv"
    log_file_name = REFERENCE_NAME + "_authors_script_log.txt" # Log specifico per questo script

    data_dir_path = get_data_dir_path(REFERENCE_NAME)
    input_csv_file_path = os.path.join(data_dir_path, input_csv_file_name)
    output_csv_file_path = os.path.join(data_dir_path, output_csv_file_name)
    log_file_path = os.path.join(data_dir_path, log_file_name)

    # API_KEY = "c81e40b973484fb83db5c697eadc3bea" # Chiave API Cast
    # API_KEY = "18acfcf2e6f1ef665eec335c2fc40fcc" # Chiave API Forlano
    # API_KEY = "10f7de16ece6898e37b7f9c6d6a68eb7" # Chiave API Caputo
    # API_KEY = "a4be5d6403465914a622246057f086e0" # Chiave API Scocco 1
    # API_KEY = "d1dd3948f277cd381a11337c51d72f67" # Chiave API Scocco 2
    # API_KEY = "2e47c27c5a96dc921842c11144168480" # Chiave API Scocco 3

    API_KEY_VALUE = "10f7de16ece6898e37b7f9c6d6a68eb7"
    PAUSE_TIME_BETWEEN_QUERIES = 0.7

    # Inizializza la struttura api_key_revolver per functions_revolver
    # Questa struttura è necessaria perché functions_revolver.get_authors_by_eid
    # utilizza internamente functions_revolver.get_next_API_key per la gestione degli errori.
    api_key_revolver = {
        "api_key": API_KEY_VALUE,
        "API_KEYS": [API_KEY_VALUE], # Anche con una sola chiave, deve essere in una lista
        "cont_key": 0,
        "cont_key_loops": 0,
        "MAX_KEY_LOOPS": 1, # Permette un ciclo per la singola chiave prima di uscire in caso di fallimento
        "log_file_path": log_file_path,
        "api_key_pause_time": PAUSE_TIME_BETWEEN_QUERIES, # Pausa dopo un cambio di chiave API (o setup iniziale)
        "api_key_roll_pause_time": 1, # Breve pausa quando si torna alla prima chiave dopo un ciclo completo
        "citation_pause_time": 0 # Non direttamente usato da get_authors_by_eid, ma parte della struttura del dizionario attesa
    }

    api_key_revolver = functions_revolver.get_next_API_key(api_key_revolver)

    # Configura il file di log per questo script
    functions_revolver.log_file_setup(log_file_path)
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"--- Inizio elaborazione: {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        f.write(f"Lettura EIDs da: {input_csv_file_path}\n")
        f.write(f"Output scritto su: {output_csv_file_path}\n")
        f.write(f"Utilizzo API Key: {API_KEY_VALUE}\n")
        f.write(f"Pausa tra le query: {PAUSE_TIME_BETWEEN_QUERIES} secondi\n\n")

    # Carica i dati esistenti dal file di output per evitare query duplicate
    existing_authors_data = {}
    if os.path.exists(output_csv_file_path):
        print(f"Trovato file esistente: {output_csv_file_path}. Caricamento dati per evitare query duplicate.")
        try:
            with open(output_csv_file_path, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='|')
                for row in reader:
                    if 'article_eid' in row and 'num_aut' in row:
                        existing_authors_data[row['article_eid']] = row['num_aut']
            print(f"Caricati {len(existing_authors_data)} record esistenti.")
        except Exception as e:
            print(f"Errore durante la lettura del file CSV esistente: {e}. Il file verrà sovrascritto.")
            existing_authors_data = {} # Resetta in caso di errore di lettura
    else:
        print("Nessun file di output esistente trovato. Tutte le query verranno eseguite.")

    print(f"Lettura EIDs dal file: {input_csv_file_path}")
    articles_data = functions_revolver.load_CSV_articles(input_csv_file_path)

    if not articles_data:
        print("Nessun articolo trovato nel CSV di input. Uscita.")
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write("Nessun articolo trovato nel CSV di input. Uscita.\n")
        return

    # output_records = []
    processed_count = 0
    total_articles = len(articles_data)

    print(f"Elaborazione di {total_articles} articoli...")

    # Determina se il file di output esiste già per decidere se scrivere l'header
    output_file_exists = os.path.exists(output_csv_file_path)

    # Apre il file di output in modalità append. I record verranno aggiunti uno alla volta.
    with open( output_csv_file_path, 'a', encoding='utf-8', newline='' ) as outfile:
        fieldnames = ["article_eid", "num_aut"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='|')

        # Scrive l'header solo se il file è stato appena creato
        if not output_file_exists:
            writer.writeheader()

        for i, article in enumerate(articles_data):
            article_eid = article.get("article_eid")
            
            if not article_eid:
                print(f"Record {i+1} saltato: 'article_eid' mancante. Record: {article}")
                with open(log_file_path, "a", encoding="utf-8") as f:
                    f.write(f"Record {i+1} saltato: 'article_eid' mancante. Record: {article}\n")
                continue
            
            if i < FIRST_ARTICLE_TO_PROCESS:
                print(f"[{i+1}/{total_articles}] EID: {article_eid} saltato (prima dell'indice di inizio).")
                continue

            # Controlla se l'EID è già stato processato in precedenza
            if article_eid in existing_authors_data:
                num_aut = existing_authors_data[article_eid]
                print(f"[{i+1}/{total_articles}] EID: {article_eid} trovato nel file esistente. Autori: {num_aut}. (Record riscritto da dati precedenti)")
                # Dato che il record è già nel file (letto in existing_authors_data), non c'è bisogno di acquisirlo di nuovo.
                # Si incrementa il contatore dei processati.
                # Scrive il singolo record nel file CSV in modalità append
                current_record = {
                    "article_eid": article_eid,
                    "num_aut": num_aut
                }
                writer.writerow(current_record)
                outfile.flush() # Forza la scrittura su disco immediata
                processed_count += 1
                continue # Salta la chiamata API e la scrittura del record          

            print(f"[{i+1}/{total_articles}] Recupero autori per EID: {article_eid}...", end="", flush=True)
            
            num_aut = "N/A" # Valore di default in caso di errore o fallimento API

            try:
                # get_authors_by_eid restituisce una lista di nomi di autori
                author_list = functions_revolver.get_authors_by_eid(article_eid, api_key_revolver)
                if isinstance(author_list, list):
                    num_aut = len(author_list)
                    print(f" Trovati {num_aut} autori.")
                else:
                    # Se get_authors_by_eid restituisce qualcosa di diverso da una lista (es. una stringa di errore)
                    print(f" Errore nel recupero autori: {author_list}")
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write(f"Errore nel recupero autori per EID {article_eid}: {author_list}\n")

            except Exception as e:
                print(f" Errore inatteso per EID {article_eid}: {e}")
                with open(log_file_path, "a", encoding="utf-8") as f:
                    f.write(f"Errore inatteso per EID {article_eid}: {e}\n")
                api_key_revolver = functions_revolver.get_next_API_key(api_key_revolver)
            
            # Scrive il singolo record nel file CSV in modalità append
            current_record = {
                "article_eid": article_eid,
                "num_aut": num_aut
            }
            writer.writerow(current_record)
            outfile.flush() # Forza la scrittura su disco immediata
            
            processed_count = processed_count + 1
            time.sleep(PAUSE_TIME_BETWEEN_QUERIES) # Pausa tra ogni chiamata API come richiesto

    print(f"\nElaborazione completata. {processed_count} record totali considerati.")
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"\n--- Elaborazione completata: {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        f.write(f"{processed_count} record totali considerati.\n")

if __name__ == "__main__":
    process_ebmc_authors()