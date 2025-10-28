import requests
import csv

# NOTA: Alcune delle funzioni in questo file dipendono da altre funzioni 
# (es. get_next_API_key, clean_field) che si trovavano nel file originale 
# 'functions_revolver.py'. Sono state archiviate qui per pulizia del codice 
# e non sono destinate all'uso diretto senza un ulteriore refactoring.

def OLD_get_citing_articles( eid, api_key):
    """
    Recupera i DOI degli articoli che citano un articolo dato.
    
    Parametri:
        api_key (str): Chiave API Elsevier.
        eid (str): EID dell'articolo da analizzare.
    
    Ritorna:
        list: Lista di DOI degli articoli citanti.
    """
    base_url = "https://api.elsevier.com/content/search/scopus"
    citing_dois = []

    start = 0
    count = 25

    while True:
        params = {
            "query": f"REF({eid})",
            "apikey": api_key,
            "view": "STANDARD",
            "start": start,
            "count": count,
        }

        try:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                entries = data.get("search-results", {}).get("entry", [])
                
                if not entries:
                    break  # Fine dei risultati
                
                for entry in entries:
                    citing_dois.append(entry.get("prism:doi", "N/A"))
                
                # Incrementa l'indicatore per ottenere la pagina successiva
                start += count
            else:
                citing_dois=[]
                #print(f"Errore nella richiesta degli articoli citanti: {response.status_code} - {response.text}")
                break
        except requests.RequestException as e:
            print(f"Errore nella richiesta: {e}")
            break

    return citing_dois

def get_reference_count_from_eid( eid, api_key_revolver ):
    """
    Ottiene il numero di riferimenti (references) in un articolo dato il suo EID.

    Parametri:
        api_key (str): La chiave API Elsevier valida.
        eid (str): L'EID dell'articolo.

    Ritorna:
        int: Numero di riferimenti, oppure -1 in caso di errore.
    """

    base_url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
    while True :
    
        actual_api_key = api_key_revolver[ "api_key"] 
        headers = {"X-ELS-APIKey": actual_api_key}
        error_text = f"\n\nThe API KEY {actual_api_key} doesn't work in fuction 'get_reference_count_from_eid'. Rolling to another API KEY"

        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            # Analizza il JSON della risposta
            data = response.json()
            reference_count = data.get("abstracts-retrieval-response", {}).get("coredata", {}).get("references-count", 0)

            # Restituisce il numero di riferimenti
            return int(reference_count)
        else:
            print( error_text )
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write( error_text )

            api_key_revolver = get_next_API_key( api_key_revolver ) # It does
                                                                    # - a try with the next API key
                                                                    # - an exit if there aren't more loops on availables API keys
            continue

def get_publication_year_using_crossref( doi ):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['message']['issued']['date-parts'][0][0]  # Extracts the year
        #return data['message']['published']['date-parts'][0][0]  # Extracts the year
    else:
        return "DOI not found or an error occurred."

def get_authors_from_doi( doi ):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        data = response.json()
        
        # Extract authors
        if "author" in data['message']:
            authors = data['message']['author']
            author_list = [f"{author.get('given', '')} {author.get('family', '')}".strip() for author in authors]
            return author_list
        else:
            print("No authors found in the metadata.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

def get_citing_articles_by_eid( eid, api_key_revolver ):
    """
    Retrieve the EIDs of articles citing a paper using its EID via the Scopus API.

    Parameters:
        eid (str): The Scopus EID of the paper.
        api_key (str): Your Elsevier API key.

    Returns:
        list: A list of EIDs of citing articles or an error message.
    """
    base_url = "https://api.elsevier.com/content/abstract/eid/"
    while True :
        actual_api_key = api_key_revolver[ "api_key"] 
        
        headers = {
            "X-ELS-APIKey": actual_api_key,
            "Accept": "application/json"
        }
        error_text = f"\n\nThe API KEY {actual_api_key} doesn't work in fuction 'get_citing_articles_by_eid'. Rolling to another API KEY"

        response = requests.get(base_url + eid + "/citedby", headers=headers)

        if response.status_code == 200:
            data = response.json()
            citing_articles = data["abstracts-retrieval-response"]["citeInfoMatrix"]["citeInfoMatrixXML"]["citation"]["ref-info"]
            citing_eids = [article["scopus-id"] for article in citing_articles if "scopus-id" in article]
            return citing_eids
        else:
            print( error_text )
            with open(api_key_revolver["log_file_path"], "a", encoding="utf-8") as file:
                file.write( error_text )

            api_key_revolver = get_next_API_key( api_key_revolver ) # It does
                                                                    # - a try with the next API key
                                                                    # - an exit if there aren't more loops on availables API keys
            continue

def manage_last_author_articles( csv_file_path , flag_CSV_last_author_delete ):
    """
    Processes a CSV file to manage the last author's entries.

    Args:
        csv_file_path (str): The path to the CSV file.

    Returns:
        tuple: A tuple containing the name, surname, and institution of the last author.
               Returns (None, None, None) if the file is empty or an error occurs.
    """

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        lines = list( csv.reader(file, delimiter="|") )       
    
    
    if not lines:
        return None, None, None
  
    # Check if the first line is the header and if the file has only one line
    first_line = lines[0]
    if first_line[0] == "Name" and len(lines) == 1:
        return None, None, None
  
    # Extract the last line's data
    last_line = lines[-1]
    last_name        = clean_field( last_line[0] )
    last_surname     = clean_field( last_line[1] )
    last_institution = clean_field( last_line[2] )

    print("\n\nLast author's data")
    print(f"Name: {last_name}\nSurname: {last_surname}\nInstitution: {last_institution}")

    # Find all lines matching the last author's data, starting from the end
    matching_lines = []
    for line in reversed(lines):
        
        n = clean_field( line[0])
        s = clean_field( line[1])
        i = clean_field( line[2])
        if (n == last_name and s == last_surname and i == last_institution):
            matching_lines.append( line )
        else:
            break

    m = len(matching_lines)
    print("\nList of the articles found for the last author\n")
    
    for k, line in enumerate( matching_lines ):
        print( f"Article n. {k+1}/{m} \n{line}\n" )

    if flag_CSV_last_author_delete :
        # Ask the user if they want to delete the matching lines
        answer = input(f"\nDo you want to delete these {m} articles? (Y/N): ")
        if answer.upper() == 'Y':
            lines_to_keep = lines [ : -m ]  # Skips the last m lines to delete them

            with open(csv_file_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(lines_to_keep)

            print(f"\n{m} articles were deleted successfully for the following author:")
            print(f"Name: {last_name}\nSurname: {last_surname}\nInstitution: {last_institution}\n")
            print(f"These articles from this author will be grabbled and added to the list in the next run\n")

        else:
            print(f"\nThe {m} articles of the last author will not be deleted.\n\n")
            last_name, last_surname, last_institution = None, None, None
        
    return last_name, last_surname, last_institution 

def is_written_author( surname, name, institution, articles_authors_unique ) :
    for k in range( len( articles_authors_unique["name"] )) :
        s = articles_authors_unique["surname"][k].lower()  
        n = articles_authors_unique["name"][k].lower()  
        i = articles_authors_unique["institution"][k].lower()        
        if (  ( surname     == s ) and 
              ( name        == n ) and 
              ( institution == i ) ) :
            return True
    return False

def articles_authors_list( csv_file_path ) :

    unique_authors_triplets = []

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter="|")
        for row in reader:
            if len(row) >= 3:  # Ensure there are at least 3 columns
                name        = clean_field( row[0] )
                surname     = clean_field( row[1] )
                institution = clean_field( row[2] )
                triplet = (name, surname, institution)
                
                if triplet not in unique_authors_triplets:
                    unique_authors_triplets.append(triplet)
    
    unique_authors_triplets = unique_authors_triplets[ 1: ] # Skips the CSV header line
    articles_authors_name_uniq        = [ triplet[0] for triplet in unique_authors_triplets]
    articles_authors_surname_uniq     = [ triplet[1] for triplet in unique_authors_triplets]
    articles_authors_institution_uniq = [ triplet[2] for triplet in unique_authors_triplets]
    
    articles_authors_unique = {
        "name"               : articles_authors_name_uniq,
        "surname"            : articles_authors_surname_uniq,
        "institution"        : articles_authors_institution_uniq }

    return articles_authors_unique

def written_article_in_CSV( articles, author_article_eid, author_name=None, author_surname=None, author_institution=None ):
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
        current_eid                = article["article_eid"]
        current_author_name        = article["name"]
        current_author_surname     = article["surname"]
        current_author_institution = article["institution"]
        if ( current_eid                == author_article_eid  ) and \
           ( current_author_name        == author_name         ) and \
           ( current_author_surname     == author_surname      ) and \
           ( current_author_institution == author_institution  ) :
            found_flag = True
            break
        if ( current_eid == author_article_eid ) :
            article_data = (    article["year"              ] , 
                                article["num_aut"           ] , 
                                article["article_refs"      ] , 
                                article["num_ref_in_citing" ] , 
                                article["citing_years"      ] )
    return found_flag,  article_data


#########################################################
# Manages the citations for the current article and returns:
# - sum of reference scores
# - list of citing years
def manage_citing_articles( author_article_citing_dois, api_key_revolver) :

    author_article_num_ref = 0.0
    author_article_citing_years = []
    citation_pause_time = api_key_revolver["citation_pause_time"]
    
    num_citing_dois = len( author_article_citing_dois )
    
    print(f"Running the {num_citing_dois} citation queries for this article")
    for k, c_doi in enumerate( author_article_citing_dois ):
        print( f"{k+1} - " , end=" " , flush=True )
        
        references, citing_year = get_crossref_data_by_doi(c_doi)

        if references and len(references) > 0:
            author_article_num_ref = author_article_num_ref + 1/len(references)
        else:
            print(f"Warning: No references found for DOI {c_doi}. Cannot calculate score. ", end="", flush=True)

        author_article_citing_years.append( citing_year )
        print(f"{citing_year} || ", end=" " , flush=True )
        time.sleep( citation_pause_time )  # Sleep for some second, to avoid hitting the API too quickly
    print("\n")
    
    return author_article_num_ref, author_article_citing_years


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
        response = requests.get(url, timeout=10)
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