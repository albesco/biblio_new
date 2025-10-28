import pandas as pd
import os

# --- CONFIGURAZIONE ---
# Imposta la directory dove si trovano i file di input e dove verrà salvato l'output.
# Lasciare la stringa vuota ('') per usare la stessa directory in cui si trova lo script.
# Esempio per una sottocartella: DIRECTORY_SOURCE = 'dati'
DIRECTORY_SOURCE = r'F:\OneDrive - Università Politecnica delle Marche\Attivita\UnivPM\20250327_Bibliometry\Dati\EBMC'

# Nomi dei file 
FILE_A_CSV = 'EBMC.csv'
FILE_B_DAT = 'campione_05.dat'
FILE_RIS_CSV = 'EBMC_Filtered.csv'
# --------------------

def filtra_csv_per_codici():
    """
    Legge i codici da B.dat, filtra le righe corrispondenti in A.csv 
    e salva il risultato in RIS.csv.
    """
    
    # Costruisce i percorsi completi dei file usando la directory specificata
    path_b_dat = os.path.join(DIRECTORY_SOURCE, FILE_B_DAT)
    path_a_csv = os.path.join(DIRECTORY_SOURCE, FILE_A_CSV)
    path_ris_csv = os.path.join(DIRECTORY_SOURCE, FILE_RIS_CSV)
    
    # --- 1. Lettura dei codici dal file B.dat ---
    try:
        with open(path_b_dat, 'r') as f:
            # Legge tutte le righe, elimina gli spazi bianchi (inclusi i newline) 
            # all'inizio e alla fine di ciascuna riga, e filtra le stringhe vuote.
            codici_da_cercare = [line.strip() for line in f if line.strip()]
        
        if not codici_da_cercare:
            print(f"ATTENZIONE: Il file {path_b_dat} è vuoto o non contiene codici validi.")
            return
            
        print(f"Letti {len(codici_da_cercare)} codici univoci da {path_b_dat}.")
        # Usiamo un set per una ricerca più efficiente e per eliminare duplicati in B.dat
        set_codici = set(codici_da_cercare)
        
    except FileNotFoundError:
        print(f"ERRORE: File {FILE_B_DAT} non trovato.")
        return
    except Exception as e:
        print(f"ERRORE durante la lettura di {path_b_dat}: {e}")
        return


    # --- 2. Lettura e elaborazione del file A.csv ---
    try:
        # Legge l'intero file CSV in un DataFrame di pandas
        df_a = pd.read_csv(path_a_csv, sep='|')
        print(f"Lette {len(df_a)} righe totali dal file {path_a_csv}.")
        
        # Verifica l'esistenza della colonna cruciale
        COLONNA_ID = 'author_id'
        if COLONNA_ID not in df_a.columns:
            print(f"ERRORE: La colonna '{COLONNA_ID}' non è stata trovata in {path_a_csv}.")
            print(f"Colonne disponibili: {list(df_a.columns)}")
            return
            
        # Assicuriamoci che la colonna sia trattata come stringa per una corretta corrispondenza
        df_a[COLONNA_ID] = df_a[COLONNA_ID].astype(str)

        # Filtro: Seleziona solo le righe dove il valore di 'author_id' è 
        # presente nell'insieme di codici 'set_codici'
        df_risultato = df_a[df_a[COLONNA_ID].isin(set_codici)]
        
        righe_trovate = len(df_risultato)
        print(f"Trovate {righe_trovate} righe corrispondenti nei codici cercati.")

        if righe_trovate == 0:
            print("Nessuna riga corrispondente trovata. Il file RIS.csv non verrà creato o verrà sovrascritto vuoto.")

    except FileNotFoundError:
        print(f"ERRORE: File {path_a_csv} non trovato.")
        return
    except Exception as e:
        print(f"ERRORE durante l'elaborazione di {path_a_csv}: {e}")
        return

    # --- 3. Scrittura del risultato in RIS.csv ---
    try:
        # Salva il DataFrame filtrato nel nuovo file CSV.
        # index=False evita che pandas scriva un indice numerico come prima colonna.
        df_risultato.to_csv(path_ris_csv, index=False, sep='|')
        print(f"Operazione completata con successo! I risultati sono stati salvati in {path_ris_csv}.")
    except Exception as e:
        print(f"ERRORE durante la scrittura di {path_ris_csv}: {e}")

# Esegui la funzione principale
if __name__ == '__main__':
 
    
    filtra_csv_per_codici()

