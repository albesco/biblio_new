import pandas as pd

# Costante per il nome del file CSV
CSV_FILE_IN  = r"C:\Users\CMM\Desktop\20250327_Bibliometry\Dati\Metallurgia\metallurgia_totale.csv"
CSV_FILE_OUT = r"C:\Users\CMM\Desktop\20250327_Bibliometry\Dati\Metallurgia\metallurgia_totale_dopo.csv"

try:
    # Leggi il file CSV utilizzando il carattere pipe come separatore
    df = pd.read_csv(CSV_FILE_IN, sep='|')

    # Ottieni il numero di righe prima dell'eliminazione
    righe_prima = len(df)

    # Elimina le righe duplicate
    df_senza_duplicati = df.drop_duplicates()

    # Ottieni il numero di righe dopo l'eliminazione
    righe_dopo = len(df_senza_duplicati)

    # Scrivi il DataFrame senza duplicati in un nuovo file CSV
    output_file = CSV_FILE_OUT
    df_senza_duplicati.to_csv(output_file, sep='|', index=False)

    print(f"File originale: {CSV_FILE_IN}")
    print(f"File senza duplicati: {CSV_FILE_OUT}")
    print(f"Numero di righe prima dell'eliminazione: {righe_prima}")
    print(f"Numero di righe dopo l'eliminazione: {righe_dopo}")
    print(f"Sono state eliminate {righe_prima - righe_dopo} righe duplicate.")

except FileNotFoundError:
    print(f"Errore: Il file '{CSV_FILE_IN}' non è stato trovato.")
except Exception as e:
    print(f"Si è verificato un errore: {e}")
