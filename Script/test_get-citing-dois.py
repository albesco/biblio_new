
# Inserisci la tua API Key di Scopus
API_KEY = "10f7de16ece6898e37b7f9c6d6a68eb7"

# EID del documento di interesse
EID = "2-s2.0-xxxxxxxxxxxx"  # Sostituisci con il tuo EID

# URL per ottenere le citazioni
url = f"https://api.elsevier.com/content/abstract/citations?scopus_id={EID}&apiKey={API_KEY}"

# Intestazioni della richiesta
headers = {
    "X-ELS-APIKey": API_KEY,
    "Accept": "application/json"
}

# Effettua la richiesta API
response = requests.get(url, headers=headers)

# Verifica la risposta
if response.status_code == 200:
    data = response.json()
    
    # Estrarre DOI dagli articoli citanti
    citing_dois = [entry.get("prism:doi", "DOI non disponibile") for entry in data.get("abstract-citations-response", {}).get("citeInfoMatrix", {}).get("citeInfo", [])]
    
    print("Lista dei DOI degli articoli citanti:")
    for doi in citing_dois:
        print(doi)

else:
    print(f"Errore {response.status_code}: {response.text}")