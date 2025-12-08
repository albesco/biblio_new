import requests
import os
import csv
import time
import pandas as pd

"""
Search for an author in Scopus by name and institution using Elsevier's API.

Parameters:
    api_key (str): Your Elsevier API key.
    first_name (str): Author's first name.
    last_name (str): Author's last name.
    institution (str): Institution name to filter the search.

Returns:
    dict: The response data from the API.
"""
def search_author_with_institution( first_name, last_name, institution, api_key_revolver ):

    # Base URL for the Scopus Author Search API
    base_url = "https://api.elsevier.com/content/search/author"
    
    # Construct the query string
    query = f"authlast({last_name}) AND authfirst({first_name}) AND affil({institution})"

    while True :
        actual_api_key = api_key_revolver[ "api_key"] 
        params = {
            "query": query,
            "apikey": actual_api_key,
            "view": "STANDARD"  # or "detailed" for more information
        }
        
        response = requests.get( base_url, params=params )
        
        if response.status_code == 200:
            return response.json()  # Parse and return an effective response as JSON
        elif response.status_code in [401, 429]:
            error_message = "is not valid" if response.status_code == 401 else "has reached the maximum number of requests"
            error_text = f"\n\nAPI KEY {actual_api_key} {error_message} \nin function 'search_author_with_institution' for the author \nFirst name: {first_name} - Last name:{last_name} - Institution: {institution}. \nRolling to another api key."
            print(error_text)
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write(error_text)
            api_key_revolver = get_next_API_key(api_key_revolver)
            continue
        elif response.status_code == 400:
            error_text = f"\n\nBad Request in 'search_author_with_institution' {response.status_code}\nFirst name: {first_name} - Last name:{last_name} - Institution: {institution}. \nIt will be skipped without roll to another API KEY."            
            print(error_text)
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write(error_text)
            return {"search-results": {"entry": [{"@_fa": "true", "error": f"Invalid input for author {first_name} {last_name}"}]}}
        else: # Gestione di altri errori 4xx o 5xx
            error_text = f"\n\nGeneric error {response.status_code}\nFirst name: {first_name} - Last name:{last_name} - Institution: {institution}. \nIt will roll to another API KEY."
            print(error_text)
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write(error_text)
            api_key_revolver = get_next_API_key(api_key_revolver)
            continue

"""
Search for an author in Scopus by name and institution using Elsevier's API.

Parameters:
    api_key (str): Your Elsevier API key.
    first_name (str): Author's first name.
    last_name (str): Author's last name.
    institution (str): Institution name to filter the search.

Returns:
    dict: The response data from the API.
"""
def search_author_with_au_id( au_id, api_key_revolver):

    # Base URL for the Scopus Author Search API
    base_url = "https://api.elsevier.com/content/search/author"
    
    # Construct the query string
    query = f"AU-ID({au_id})"
            
    while True :
        actual_api_key = api_key_revolver[ "api_key"] 
        params = {
            "query": query,
            "apikey": actual_api_key,
            "view": "STANDARD"  # or "detailed" for more information
        }
        response = requests.get( base_url, params=params )
        
        if response.status_code == 200:
            return response.json()  # Parse and return an effective response as JSON
        elif response.status_code == 401:
            error_text = f"\n\nAPI KEY {actual_api_key} non valida o scaduta in 'search_author_with_au_id' per AU-ID {au_id}. Tentativo con un'altra API KEY."
            print(error_text)
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write(error_text)
            api_key_revolver = get_next_API_key(api_key_revolver)
            continue # Riprova con la nuova chiave
        elif response.status_code == 429:
            error_text = f"\n\nAPI KEY {actual_api_key} ha superato il limite di richieste in 'search_author_with_au_id' per AU-ID {au_id}. Tentativo con un'altra API KEY."
            print(error_text)
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write(error_text)
            api_key_revolver = get_next_API_key(api_key_revolver)
            continue # Riprova con la nuova chiave
        elif response.status_code == 400:
            error_text = f"\n\nInput non valido (Bad Request) in 'search_author_with_au_id' per AU-ID {au_id}. Dettagli: {response.text}. Non si tenterà con un'altra API KEY per questo errore."
            print(error_text)
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write(error_text)
            # Un input non valido non è un problema di API key, quindi non ha senso ruotare.
            # Potresti voler restituire un dizionario di errore specifico o sollevare un'eccezione.
            return {"search-results": {"entry": [{"@_fa": "true", "error": f"Invalid input for AU-ID {au_id}"}]}}
        else: # Gestione di altri errori 4xx o 5xx
            error_text = f"\n\nErrore generico {response.status_code} in 'search_author_with_au_id' per AU-ID {au_id}. Dettagli: {response.text}. Tentativo con un'altra API KEY."
            print(error_text)
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write(error_text)
            api_key_revolver = get_next_API_key(api_key_revolver)
            continue # Riprova con la nuova chiave

"""
Recupera gli articoli di un autore usando lo Scopus Author ID.

Parametri:
    api_key (str): Chiave API Elsevier.
    author_id (str): Scopus Author ID dell'autore.

Ritorna:
    list: Lista di articoli con dettagli sugli autori, citazioni e DOI.
"""        
def get_author_articles( author_id, api_key_revolver ):

    base_url = "https://api.elsevier.com/content/search/scopus"
    articles = []
    start = 0  # Indicatore per la paginazione
    count = 200  # Numero massimo di articoli per pagina (fino a 200)

    loop_batches_flag = True
    while loop_batches_flag:     # Loop for the query batches

        while True :    # Loop for the API keys
            actual_api_key = api_key_revolver[ "api_key"] 

            params = {
                "query": f"AU-ID({author_id})",  # Filtra per Author ID
                "apikey": actual_api_key,
                "view": "STANDARD",
                "start": start,
                "count": count,
            }   
            
            response = requests.get( base_url, params=params )         

            error_text = f"\n\nThe API KEY {actual_api_key} doesn't work in fuction 'get_author_articles'. Rolling to another API KEY"
         
            if response.status_code == 200:
                data = response.json()
                entries = data.get("search-results", {}).get("entry", [])
                
                if not entries:
                    loop_batches_flag = False
                    break  # Fine dei risultati
                
                for entry in entries:
                    # Recupera i dettagli per ogni articolo
                    article = {
                        "title": entry.get("dc:title", "N/A"),
                        #"num_authors": len(entry.get("author", [])),  # Conteggio autori
                        "num_authors": len(entry.get("author", "N/A")),  # Conteggio autori
                        
                        "num_citations": int(entry.get("citedby-count", 0)),
                        "doi": entry.get("prism:doi", "N/A"),
                        "eid": entry.get("eid", "N/A"),  # EID per richieste aggiuntive
                    }
                    articles.append(article)
                
                # Incrementa l'indicatore per la pagina successiva
                start = start + count
                time.sleep(api_key_revolver.get("pagination_pause_time", 0.5)) # Pausa tra le pagine
            else:
                print( error_text )
                with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                    file.write( error_text )

                api_key_revolver = get_next_API_key( api_key_revolver ) # It does
                                                                        # - a try with the next API key
                                                                        # - an exit if there aren't more loops on availables API keys  
                continue

    return articles

"""
Recupera i DOI degli articoli che citano un articolo dato.

Parametri:
    api_key (str): Chiave API Elsevier.
    eid (str): EID dell'articolo da analizzare.

Ritorna:
    list: Lista di DOI degli articoli citanti.
"""
def get_citing_articles( eid, api_key_revolver):

    base_url = "https://api.elsevier.com/content/search/scopus"
    start = 0
    step = 25

    citing_dois = []    
    while True:  # Loop per la paginazione (loop_batches_flag)
        request_successful = False
        while not request_successful:  # Loop per la gestione delle chiavi API
            actual_api_key = api_key_revolver["api_key"]
            params = {
                "start": start,
                "count": step,
                "apikey": actual_api_key,
                "query": f"REF({eid})",
                "view": "STANDARD"
            } 

            try:
                response = requests.get(base_url, params=params, timeout=120)
                
                if response.status_code == 200:
                    data = response.json()
                    entries = data.get("search-results", {}).get("entry", [])
                    
                    # Scopus può restituire una lista vuota o una lista con un singolo elemento di errore.
                    # Controlliamo entrambi i casi.
                    if not entries or (len(entries) == 1 and entries[0].get("error") == "Result set was empty"):
                        # Non ci sono più risultati, la paginazione è completa.
                        return citing_dois
                    
                    for entry in entries:
                        res = entry.get("prism:doi")
                        if res:
                            citing_dois.append(res)
                    
                    request_successful = True  # La richiesta per questa pagina è andata a buon fine.

                elif response.status_code >= 400:
                    error_text = f"\n\nAPI KEY {actual_api_key} failed in function 'get_citing_articles' for EID {eid}. Rolling to another API KEY"
                    print(error_text)
                    with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                        file.write(error_text)
                    api_key_revolver = get_next_API_key(api_key_revolver)
                    # 'continue' nel ciclo 'while not request_successful' per riprovare con la nuova chiave.
            except requests.exceptions.RequestException as e:
                print(f"\nNetwork error in 'get_citing_articles' for EID {eid}: {e}. Retrying with next API key.")
                api_key_revolver = get_next_API_key(api_key_revolver)

        if request_successful:
            start += step  # Passa alla pagina successiva solo se la richiesta è andata a buon fine
            time.sleep(api_key_revolver.get("pagination_pause_time", 0.5)) # Pausa tra le pagine

    return citing_dois

"""
Recupera gli EID degli articoli che citano un articolo dato.

Parametri:
    eid (str): EID dell'articolo da analizzare.
    api_key_revolver (dict): Dizionario per la gestione delle chiavi API.

Ritorna:
    list: Lista di EID degli articoli citanti.
"""
def get_citing_articles_EID( eid, api_key_revolver):

    base_url = "https://api.elsevier.com/content/search/scopus"
    start = 0
    step = 25

    citing_eids = []
    while True:  # Loop per la paginazione
        request_successful = False
        while not request_successful:  # Loop per la gestione delle chiavi API
            actual_api_key = api_key_revolver["api_key"]
            params = {
                "start": start,
                "count": step,
                "apikey": actual_api_key,
                "query": f"REF({eid})",
                "view": "STANDARD"
            }

            try:
                response = requests.get(base_url, params=params, timeout=120)

                if response.status_code == 200:
                    data = response.json()
                    entries = data.get("search-results", {}).get("entry", [])

                    if not entries or (len(entries) == 1 and entries[0].get("error") == "Result set was empty"):
                        return citing_eids

                    for entry in entries:
                        res = entry.get("eid")
                        if res:
                            citing_eids.append(res)

                    request_successful = True

                elif response.status_code >= 400:
                    error_text = f"\n\nAPI KEY {actual_api_key} failed in function 'get_citing_articles_EID' for EID {eid}. Rolling to another API KEY"
                    print(error_text)
                    with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                        file.write(error_text)
                    api_key_revolver = get_next_API_key(api_key_revolver)
            except requests.exceptions.RequestException as e:
                print(f"\nNetwork error in 'get_citing_articles_EID' for EID {eid}: {e}. Retrying with next API key.")
                api_key_revolver = get_next_API_key(api_key_revolver)

        if request_successful:
            start += step
            time.sleep(api_key_revolver.get("pagination_pause_time", 0.5)) # Pausa tra le pagine

"""
Ottiene il numero di riferimenti (references) in un articolo dato il suo EID.

Parametri:
    eid (str): L'EID dell'articolo.
    api_key_revolver (dict): Dizionario per la gestione delle chiavi API.

Ritorna:
    int: Numero di riferimenti, oppure -1 in caso di errore o dati mancanti.
"""
def get_num_references_from_eid(eid, api_key_revolver):    
    base_url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
    while True:
        actual_api_key = api_key_revolver["api_key"]
        headers = {
            "X-ELS-APIKey": actual_api_key,
            "Accept": "application/json"
        }
        params = {
            "view": "FULL"  # Richiede la vista completa per includere il reference-count
        }
        error_text = f"\n\nThe API KEY {actual_api_key} failed in function 'get_num_references_from_eid' for EID {eid}. Rolling to another API KEY"

        try:
            # Aggiungi i parametri alla richiesta
            response = requests.get(base_url, headers=headers, params=params, timeout=120)
            if response.status_code == 200:
                data = response.json()
                # Con view=FULL, l'API restituisce l'intera lista senza paginazione.
                try:
                    references = data.get("abstracts-retrieval-response", {}).get("item", {}).get("bibrecord", {}).get("tail", {}).get("bibliography", {}).get("reference", [])
                    # La risposta potrebbe contenere un singolo dizionario invece di una lista se c'è una sola referenza
                    if isinstance(references, dict):
                        return 1
                    return len(references) if references else 0
                except (AttributeError, TypeError):
                    # Fallback nel caso la struttura JSON non sia quella attesa
                    return 0
            else:
                print(error_text)
                with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                    file.write(error_text)
                api_key_revolver = get_next_API_key(api_key_revolver)  # Riprova con la nuova chiave
                continue
        except requests.exceptions.RequestException as e: # Errore di rete
            print(f"\nNetwork error in 'get_num_references_from_eid' for EID {eid}: {e}. Retrying with next API key.")
            api_key_revolver = get_next_API_key(api_key_revolver)
            continue

"""
Ottiene l'anno di pubblicazione e il numero di referenze di un articolo dato il suo EID.
Questa funzione è ottimizzata per recuperare più dettagli con una sola chiamata API.

Parametri:
    eid (str): L'EID dell'articolo.
    api_key_revolver (dict): Dizionario per la gestione delle chiavi API.

Ritorna:
    tuple: Una tupla contenente (anno, numero_di_referenze).
           Restituisce (None, 0) in caso di errore o dati mancanti.
"""
def get_details_from_eid(eid, api_key_revolver):
    base_url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
    while True:
        actual_api_key = api_key_revolver["api_key"]
        headers = {"X-ELS-APIKey": actual_api_key, "Accept": "application/json"}
        params = {"view": "FULL"}
        error_text = f"\n\nThe API KEY {actual_api_key} failed in function 'get_details_from_eid' for EID {eid}. Rolling to another API KEY"

        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=120)
            if response.status_code == 200:
                data = response.json().get("abstracts-retrieval-response", {})
                
                # Estrai anno
                year_str = data.get("coredata", {}).get("prism:coverDate", "").split("-")[0]
                year = int(year_str) if year_str.isdigit() else None

                # Estrai numero di referenze contando gli elementi
                references = data.get("item", {}).get("bibrecord", {}).get("tail", {}).get("bibliography", {}).get("reference", [])
                if isinstance(references, dict):
                    ref_count = 1
                else:
                    ref_count = len(references) if references else 0
                
                return year, ref_count
            elif response.status_code == 429:
                print(error_text+" - Rate limit of queries exceeded."  )
                with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                    file.write(error_text)
                api_key_revolver = get_next_API_key(api_key_revolver)
                continue
            
            elif response.status_code == 404:
                year = -1
                ref_count = -1
                error_text = f" Not Found error (404) in 'get_details_from_eid' for EID {eid}. Article not found. Returning (-1, -1)."
                print(error_text)
                with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                    file.write(error_text)
                return year, ref_count
            else:
                print(error_text)
                with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                    file.write(error_text)
                api_key_revolver = get_next_API_key(api_key_revolver)
                continue
        except requests.exceptions.Timeout as e:
            year = -1
            ref_count = -1
            error_text = f"\n\nTimeout error in 'get_details_from_eid' for EID {eid}: {e}. Returning (-1, -1)."
            print(error_text)
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write(error_text)
            return year, ref_count
        except requests.exceptions.RequestException as e:
            print(f"\nNetwork error in 'get_details_from_eid' for EID {eid}: {e}. Retrying with next API key.")
            api_key_revolver = get_next_API_key(api_key_revolver)
            continue

"""
Recupera l'anno di pubblicazione di un articolo dato il suo DOI usando l'API di Elsevier.

Parameters:
    doi (str): Il DOI dell'articolo.
    api_key (str): La tua chiave API di Elsevier.

Returns:
    str: L'anno di pubblicazione (YYYY), oppure None in caso di errore.
"""
def get_publication_year_using_scopus(doi, api_key_revolver ):

    base_url = "https://api.elsevier.com/content/search/scopus"
    params = {
        "query": f"DOI({doi})",
        "view": "COMPLETE"
    }
    while True :
        actual_api_key = api_key_revolver[ "api_key"] 
        headers = {
            "X-ELS-APIKey": actual_api_key ,
            "Accept": "application/json"  # Richiedi la risposta in formato JSON
        }

        error_text = f"\n\nThe API KEY {actual_api_key} doesn't work in fuction 'get_publication_year_using_scopus'. Rolling to another API KEY"
       

        
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            entries = data.get("search-results", {}).get("entry", [])
            if entries:
                cover_date = entries[0].get("prism:coverDate")
                if cover_date:
                    return int(cover_date[:4])  # Estrae i primi 4 caratteri (l'anno)
            return None

        else:
            print( error_text )
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write( error_text )

            api_key_revolver = get_next_API_key( api_key_revolver ) # It does
                                                                    # - a try with the next API key
                                                                    # - an exit if there aren't more loops on availables API keys
            continue

"""
Recupera le referenze e l'anno di pubblicazione di un articolo usando l'API di Crossref.

Parameters:
    doi (str): Il DOI dell'articolo.

Returns:
    tuple: Una tupla contenente (lista_referenze, anno_pubblicazione).
            Restituisce (None, None) in caso di errore o dati mancanti.
"""
def get_crossref_data_by_doi(doi):

    if not doi or not isinstance(doi, str):
        return None, None

    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()

        data = response.json()
        message = data.get('message', {})

        # Estrai le referenze
        references = message.get('reference')

        # Estrai l'anno di pubblicazione
        publication_year = None
        if 'published' in message:
            date_parts = data['message']['published'].get('date-parts', [[]])
            if date_parts and date_parts[0]:
                publication_year = int(date_parts[0][0])

        return references, publication_year
    except requests.exceptions.RequestException as e:
        print(f"Errore nella chiamata a Crossref per il DOI {doi}: {e}")
        return None, None

"""
Retrieve the list of authors for a paper using its EID via the Scopus API.

Parameters:
    eid (str): The Scopus EID of the paper.
    api_key (str): Your Elsevier API key.

Returns:
    list: A list of author names or an error message.
"""
def get_authors_by_eid( eid, api_key_revolver ):
    """
    Retrieve the list of authors for a paper using its EID via the Scopus API.

    Parameters:
        eid (str): The Scopus EID of the paper.
        api_key (str): Your Elsevier API key.

    Returns:
        list: A list of author names or an error message.
    """
    base_url = "https://api.elsevier.com/content/abstract/eid/"
    while True:
        actual_api_key = api_key_revolver[ "api_key"] 
        headers = {
            "X-ELS-APIKey": actual_api_key,
            "Accept": "application/json"
        }
        error_text = f"\n\nThe API KEY {actual_api_key} doesn't work in fuction 'get_authors_by_eid'. Rolling to another API KEY"

        response = requests.get(base_url + eid, headers=headers)

        if response.status_code == 200:
            data = response.json()
            authors = data["abstracts-retrieval-response"]["authors"]["author"]
            author_list = [author["ce:indexed-name"] for author in authors]
            return author_list
        else:
            print( error_text )
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write( error_text )

            api_key_revolver = get_next_API_key( api_key_revolver ) # It does
                                                                    # - a try with the next API key
                                                                    # - an exit if there aren't more loops on availables API keys
            continue

"""
Retrieve the year of publication for a paper using its EID via the Scopus API.

Parameters:
    eid (str): The Scopus EID of the paper.
    api_key (str): Your Elsevier API key.

Returns:
    str: The year of publication or an error message.
"""
def get_article_year_by_eid( eid, api_key_revolver):

    base_url = "https://api.elsevier.com/content/abstract/eid/"
    
    while True :
        actual_api_key = api_key_revolver[ "api_key"] 
        
        headers = {
            "X-ELS-APIKey": actual_api_key,
            "Accept": "application/json"
        }

        response = requests.get( base_url + eid, headers=headers)
        error_text = f"\n\nThe API KEY {actual_api_key} doesn't work in fuction 'get_article_year_by_eid'. Rolling to another API KEY"
       

        if response.status_code == 200:
            data = response.json()
            year = data["abstracts-retrieval-response"]["coredata"]["prism:coverDate"].split("-")[0]
            return year
        else:
            print( error_text )
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write( error_text )

            api_key_revolver = get_next_API_key( api_key_revolver ) # It does
                                                                    # - a try with the next API key
                                                                    # - an exit if there aren't more loops on availables API keys
            continue

############################################################
# Retrieves the list of references for a given DOI using the Crossref API.
# Returns the list of references if available, otherwise returns a message or error.
def get_references_by_doi( doi ):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'reference' in data['message']:
            references = data['message']['reference']
            return references
        else:
            return "No references available for this DOI."
    else:
        return f"Error: {response.status_code} - {response.text}"
    
"""
Queries the Scopus API to retrieve publication years and reference counts for a list of DOIs.
This function processes a list of citing DOIs, making individual API calls to Scopus to obtain
publication metadata. It implements API key rotation mechanism to handle rate limits and authentication
failures. For each DOI, it retrieves the publication year from the cover date and the number of
references through a separate function call.
    citing_dois (list): List of DOIs (Digital Object Identifiers) for the citing articles.
    api_key_revolver (dict): Dictionary containing API key management information including:
        - 'api_key': Current active API key
        - 'log_file_path': Path to the log file for API errors
    tuple: Contains two lists:
        - publication_years (list): List of publication years (int or None if not found)
        - reference_counts (list): List of reference counts (int, 0 if not found)
Notes:
    - Implements error handling for API requests
    - Includes automatic API key rotation on failure
    - Adds 1-second delay between requests to respect API rate limits
    - Logs API key failures to specified log file
"""
def get_scopus_data_for_citing_dois(citing_dois, api_key_revolver):

    """
    Per una lista di DOI, interroga l'API di Scopus per ottenere l'anno di pubblicazione e il numero di referenze.

    Parameters:
        citing_dois (list): Una lista di DOI degli articoli citanti.
        api_key_revolver (dict): L'oggetto per la gestione delle chiavi API.

    Returns:
        tuple: Una tupla contenente due liste:
               - publication_years (list): La lista degli anni di pubblicazione.
               - reference_counts (list): La lista del numero di referenze per ciascun articolo.
    """
    publication_years = []
    reference_counts = []
    base_url = "https://api.elsevier.com/content/search/scopus"

    print(f"Running {len(citing_dois)} Scopus queries for citing articles...")
    for i, doi in enumerate(citing_dois):
        print(f"{i+1} - ", end="", flush=True)
        
        # Valori di default in caso di fallimento o dati mancanti
        year = None
        ref_count = 0
        citation_pause_time = api_key_revolver["citation_pause_time"]

        while True:  # Loop per la gestione delle chiavi API
            actual_api_key = api_key_revolver["api_key"]
            params = {
                "query": f"DOI({doi})",
                "apikey": actual_api_key,
                "view": "COMPLETE",  # La vista STANDARD è sufficiente per anno e conteggio referenze
                "field": "prism:coverDate,citedby-count,prism:doi,eid,refcount" # Campi specifici per ottimizzare la risposta
            }

            try:
                response = requests.get(base_url, params=params, timeout=120)

                if response.status_code == 200:
                    data = response.json()
                    entry = data.get("search-results", {}).get("entry", [{}])[0]
                    
                    # Estrai l'anno di pubblicazione
                    cover_date = entry.get("prism:coverDate")
                    if cover_date:
                        year = int(cover_date.split('-')[0])
                    
                    # Estrai il numero di referenze
                    ref_list = get_references_by_doi( doi )
                    ref_count = len (ref_list) if isinstance(ref_list, list) else 0
                    
                    print(f"Year: {year}, Refs: {ref_count} || ", end="", flush=True)
                    break  # Esce dal loop delle chiavi API se la richiesta ha successo

                elif response.status_code >= 400:
                    error_text = f"\nAPI KEY {actual_api_key} failed in 'get_scopus_data_for_citing_dois' for DOI {doi}. Rolling to next key."
                    print(error_text)
                    with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                        file.write(error_text)
                    
                    api_key_revolver = get_next_API_key(api_key_revolver)
                    continue # Riprova la stessa richiesta con la nuova chiave

            except requests.exceptions.RequestException as e:
                print(f"\nRequest failed for DOI {doi}: {e}. Skipping this DOI.")
                break # Esce dal loop delle chiavi e passa al DOI successivo

        publication_years.append(year)
        reference_counts.append(ref_count)
        time.sleep( citation_pause_time ) # Pausa per rispettare i limiti dell'API

    print("\nScopus queries completed for this article.")
    return publication_years, reference_counts

#####################################################
# Gets a string that contains the words contained in the name and surname, and compose them considering that 
# - the words for name are all lowercase 
# - the words for surname are all uppercase 
def extract_surname_and_name( full_name  ):
    if ( full_name is None ) or ( not isinstance( full_name, str ) ) or ( full_name == "" ) :
        return None, None
    surname_words = []
    name_words    = []
    words_in_full_name = full_name.split()
    if not words_in_full_name:
        return None, None

    for word in words_in_full_name: # Identify surname words (all uppercase)
        if word.isupper():
            surname_words.append(word)
        else:
            break
    
    name_words = words_in_full_name[ len(surname_words): ] # Identify name words (all lowercase or title case)

    if not surname_words or not name_words:
        return None, None

    surname = " ".join( surname_words )
    surname = surname.lower()

    # Format name words to title case
    formatted_name_words = [word.capitalize() for word in name_words]
    name = " ".join(formatted_name_words)

    return surname, name

####################################################
# Erase all the blank, the " and the ' characters in the string parameter
def clean_field(field):
    """
    Cleans a field by removing leading/trailing whitespace, double quotes, and single quotes only at the start or end of the string.
    Single and double quotes inside the string are preserved.

    Args:
        field (str): The field to clean.

    Returns:
        str: The cleaned field.
    """

    if isinstance(field, str):
        if not field:
            return []
        else:
            field = field.strip()
    elif isinstance(field, list):
        field = [clean_field(item) for item in field]
        return field
    elif isinstance(field, (int, float )):
        return field

    else:
        return None
    
    field = field.lower()
    flag_ok = False
    while not ( flag_ok ) :
        if field.startswith('"') :
            field = field[ 1: ]
            continue
        if field.endswith('"'):
            field = field[  :-1]
            continue
        if field.startswith("'") :
            field = field[ 1: ]
            continue
        if field.endswith("'"):
            field = field[  :-1]
            continue
        flag_ok = True

    return field

#################################################################
# Clears the CSV file from wrong string special-characters, as single and double quotes 
def csv_file_cleaning( csv_file_path ):

    articles_authors_name        = []
    articles_authors_surname     = []
    articles_authors_institution = []
    articles_authors_author_id   = []
    articles_authors_article_eid = []
    articles_authors_year        = []
    articles_authors_num_aut     = []
    articles_authors_num_cit     = []
    articles_authors_article_refs= []
    articles_authors_citing_years = []
    articles_authors_num_ref_in_citing= []

    with open( csv_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            ls = line.strip()

            data_row = ls.split('|')
            articles_authors_name.append(               clean_field( data_row[0] ) )
            articles_authors_surname.append(            clean_field( data_row[1] ) )
            articles_authors_institution.append(        clean_field( data_row[2] ) )
            articles_authors_author_id.append(          clean_field( data_row[3] ) )
            articles_authors_article_eid.append(        clean_field( data_row[4] ) )
            articles_authors_year.append(               clean_field( data_row[5] ) )
            articles_authors_num_aut.append(            clean_field( data_row[6] ) )
            articles_authors_num_cit.append(            clean_field( data_row[7] ) )
            articles_authors_article_refs.append(       clean_field( data_row[8] ) )
            articles_authors_num_ref_in_citing.append(  clean_field( data_row[9] ) )
            # The citing years contain the character "," so split breaks this string into substrings
            # That's why it is necessary to join together the strings from the 10th position till the end of the list
            articles_authors_citing_years.append( clean_field( ','.join( data_row[10:] ) ) )

    articles = {
        "name"               : articles_authors_name,
        "surname"            : articles_authors_surname,
        "institution"        : articles_authors_institution,
        "author_id"          : articles_authors_author_id,
        "article_eid"        : articles_authors_article_eid,
        "year"               : articles_authors_year,
        "num_aut"            : articles_authors_num_aut,
        "num_cit"            : articles_authors_num_cit,
        "article_refs"       : articles_authors_article_refs,
        "num_ref_in_citing"  : articles_authors_num_ref_in_citing,
        "citing_years"       : articles_authors_citing_years }

    with open( csv_file_path, "w", encoding="utf-8", newline="" ) as file:
        writer = csv.DictWriter(file, delimiter="|", fieldnames=["name", "surname", "institution", "author_id", "article_eid", "year", "num_aut", "num_cit", "article_refs", "num_ref_in_citing", "citing_years"])       
        writer.writerows( [ {
            "name"               : articles["name"][k],
            "surname"            : articles["surname"][k],
            "institution"        : articles["institution"][k],
            "author_id"          : articles["author_id"][k],
            "article_eid"        : articles["article_eid"][k],
            "year"               : articles["year"][k],
            "num_aut"            : articles["num_aut"][k],
            "num_cit"            : articles["num_cit"][k],
            "article_refs"       : articles["article_refs"][k],
            "num_ref_in_citing"  : articles["num_ref_in_citing"][k],
            "citing_years"       : articles["citing_years"][k] } 
            for k in range( len( articles["name"] ) ) ] )

############################################################
# Sets up the log file with the time marker
def log_file_setup( log_file_path ):
    if os.path.exists(log_file_path):
        open_parameter = "a"
        print(f"\n\nLog file {log_file_path} already exists. It will be appended")  
    else : 
        open_parameter = "w"
        print(f"\n\nLog file {log_file_path} does not exist. It will be created")
    
    with open(log_file_path, open_parameter , encoding="utf-8" ) as file:
        file.write( "##############################\n" )
        file.write( "##############################\n" )
        file.write( time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" )
        file.write( "##############################\n" )
        file.write( "##############################\n\n" )
            
############################################################
# Sets up the log file with the time marker
def skipped_file_setup( skipped_file_path ):
    if os.path.exists( skipped_file_path):
        open_parameter = "a"
        print(f"\n\nSkipped authors file { skipped_file_path} already exists. It will be appended")  
    else : 
        open_parameter = "w"
        print(f"\n\nSkipped authors file {skipped_file_path} does not exist. It will be created")
    
    with open( skipped_file_path, open_parameter , encoding="utf-8" ) as file:
        file.write( "##############################\n" )
        file.write( "##############################\n" )
        file.write( time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" )
        file.write( "##############################\n" )
        file.write( "##############################\n\n" )

###########################################################
# Sets up the CSV file by 
# - creating it if it doesn't exist 
# - writing the header if it's empty
# - cleaning it from wrong characters (single and double quotes)
def CSV_file_setup( csv_file_path,  ):
    if not os.path.exists(csv_file_path):
        print(f"\n\nCSV file {csv_file_path} does not exist. It will be created")
        with open(csv_file_path, "w", encoding="utf-8", newline="") as file:
            pass

    if os.stat(csv_file_path).st_size == 0:
        print(f"\n\nCSV file {csv_file_path} hasn't the header. It will be written in the first row")
        with open(csv_file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, delimiter="|", fieldnames=["name", "surname", "institution", "author_id", "article_eid", "year", "num_aut", "num_cit", "article_refs", "num_ref_in_citing", "citing_years"])       
            writer.writeheader()    

############################################################
# Creates a list of authors from the XLS file, and adds the last author to it if it is not already present
def XLS_authors_list( xls_file_path ):

    XLS_authors = {
        "name": [],
        "surname": [],
        "institution": [],
        "au_id": []
    }

    df = pd.read_excel(xls_file_path)
    col_surname_name = df['Cognome e Nome']
    col_institution = df['Ateneo']
    # Gestisce correttamente i valori vuoti (NaN) nella colonna AU_ID.
    # 1. Riempie i NaN con una stringa vuota.
    # 2. Converte tutta la colonna in stringa.
    # 3. Rimuove il ".0" finale che pandas aggiunge ai numeri letti come float.
    col_au_id = df['AU_ID'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True)

    for k in range(len(col_surname_name)):
        XLS_authors["institution"].append(str(col_institution[k]).lower())
        s_n = col_surname_name[k]
        s, n = extract_surname_and_name(s_n)
        XLS_authors["surname"].append(s.lower() if s else "")
        XLS_authors["name"].append(n.lower() if n else "")
        XLS_authors["au_id"].append(col_au_id[k].lower())

    return XLS_authors

#########################################################
# Reads a CSV file and returns its content as an array of dictionaries.
# Each dictionary represents a row in the CSV file.
def load_CSV_articles( csv_file_path ):
    """
    Reads a CSV file and returns its content as an array of dictionaries.

    Args:
        csv_file_path (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row in the CSV.
              Returns an empty list if the file is empty or an error occurs.
    """
    data = []
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader( file, delimiter='|' )  # Assuming '|' as the delimiter
            if reader.fieldnames is None:
                print(f"Warning: The file {csv_file_path} is empty or does not have a header.")
                return []
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: File not found at {csv_file_path}")
        return []
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return []
    return data

################################################################
# Checks if the article is already written in the CSV file
# and if it is, it returns True
def written_article_in_CSV_Scopus( articles, author_article_eid, author_id_Scopus=None ):
    """
    Checks if a given article (identified by EID) is already present in the list of articles.
    It also checks if the article is already associated with a specific author (name, surname, institution).

    Args:
        articles (list): A list of dictionaries, where each dictionary represents an article.
        author_article_eid (str): The EID of the article to check.
        author_name (str, optional): The name of the author. Defaults to None.
        author_surname (str, optional): The surname of the author. Defaults to None.
        author_institution (str, optional): The institution of the author. Defaults to None.

    Returns:
        tuple: A tuple containing:
            - bool: True if the article is found (and optionally, associated with the author), False otherwise.
            - tuple or None: If the article is found, returns a tuple of its data (year, num_aut, article_refs, num_ref_in_citing, citing_years).
                             Returns None if the article is not found or if it's found for the exact same author.
    """
    
    article_data = None
    found_flag   = False
    
    if not articles:  # Check if the list is empty
        return False, article_data

    for article in articles:
        current_eid                = article[ "article_eid" ]
        current_author_id          = article[ "author_id"   ]
        if ( current_eid        == author_article_eid  ) and \
           ( current_author_id  == author_id_Scopus    ) :
                found_flag   = True
                article_data = (    article["year"              ] , 
                                    article["num_aut"           ] , 
                                    article["article_refs"      ] , 
                                    article["num_ref_in_citing" ] , 
                                    article["citing_years"      ] )
                break            

    return found_flag,  article_data

"""
Manages API key rotation by cycling through a list of available keys with a maximum number of rotation loops.
This function handles the rotation of API keys when API call limits are reached. It keeps track of
how many times the key list has been cycled through and implements waiting periods between cycles.
Parameters
----------
api_key_revolver : dict
    A dictionary containing:
        - API_KEYS (list): List of available API keys
        - cont_key (int): Current key index
        - cont_key_loops (int): Number of complete rotations through the key list
        - MAX_KEY_LOOPS (int): Maximum allowed number of complete rotations
        - log_file_path (str): Path to the log file
        - api_key (str): Current active API key
Returns
-------
dict
    Updated api_key_revolver dictionary with new key and counters
Notes
-----
- Implements a 5-minute wait period when cycling back to the first key
- Implements a 10-second wait period after each key change
- Logs all key changes to both console and file
- Exits with code 1 if MAX_KEY_LOOPS is exceeded
"""
def get_next_API_key( api_key_revolver ) :

    API_KEYS           = api_key_revolver["API_KEYS"]
    cont_key           = api_key_revolver["cont_key"]
    cont_key_loops     = api_key_revolver["cont_key_loops"]
    MAX_KEY_LOOPS      = api_key_revolver["MAX_KEY_LOOPS"]
    api_key_pause_time      = api_key_revolver["api_key_pause_time"]
    api_key_roll_pause_time = api_key_revolver["api_key_roll_pause_time"]


    cont_key = cont_key + 1
    if cont_key >= len( API_KEYS ):
        
        time.sleep( api_key_roll_pause_time )  # Sleep for 5 minutes, after the completion of the trial set, before trying the first API key again
        if cont_key_loops <= MAX_KEY_LOOPS :
            cont_key_loops = cont_key_loops + 1
            cont_key = 0
            
        else :
            print(f"\n\nAll the trial made with the single API KEYS were unsuccessfull. It needs to verify the API Calls limit.")                    
            with open( api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write(f"\n\nAll the trial made with the single API KEYS were unsuccessfull. It needs to verify the API Calls limit.")                    
            exit(1)
    
    api_key_revolver["api_key"]        = API_KEYS[cont_key]
    api_key_revolver["cont_key"]       = cont_key
    api_key_revolver["cont_key_loops"] = cont_key_loops
    
    ############# Log the API key change ##################
    print("\nRolling to the next API KEY: ", api_key_revolver["api_key"] )
    print(f"cont_key: {cont_key} - cont_key_loops: {cont_key_loops}\n")
    with open( api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
        file.write(f"\nRolling to the next API KEY: {api_key_revolver['api_key']}\n")
        file.write(f"cont_key: {cont_key} - cont_key_loops: {cont_key_loops}\n")

    time.sleep( api_key_pause_time )
    return api_key_revolver