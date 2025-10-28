import requests
import os
import csv
import time


def search_author_with_institution( first_name, last_name, institution, api_key):
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
    # Base URL for the Scopus Author Search API
    base_url = "https://api.elsevier.com/content/search/author"
    
    # Construct the query string
    query = f"authlast({last_name}) AND authfirst({first_name}) AND affil({institution})"
    
    # API parameters
    params = {
        "query": query,
        "apikey": api_key,
        "view": "STANDARD"  # or "detailed" for more information
    }
    
    try:
        # Make the API request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()  # Parse response as JSON
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred searching with Name, Surname, Institution: {e}")
        return None


def search_author_with_au_id( au_id, api_key):
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
    # Base URL for the Scopus Author Search API
    base_url = "https://api.elsevier.com/content/search/author"
    
    # Construct the query string
    query = f"AU-ID({au_id})"
    
    # API parameters
    params = {
        "query": query,
        "apikey": api_key,
        "view": "STANDARD"  # or "detailed" for more information
    }
    
    try:
        # Make the API request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()  # Parse response as JSON
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred searching with AU_ID: {e}")
        return None
    

def get_author_articles( author_id, api_key ):
    """
    Recupera gli articoli di un autore usando lo Scopus Author ID.
    
    Parametri:
        api_key (str): Chiave API Elsevier.
        author_id (str): Scopus Author ID dell'autore.
    
    Ritorna:
        list: Lista di articoli con dettagli sugli autori, citazioni e DOI.
    """
    base_url = "https://api.elsevier.com/content/search/scopus"
    articles = []
    start = 0  # Indicatore per la paginazione
    count = 200  # Numero massimo di articoli per pagina (fino a 25)

    while True:
        params = {
            "query": f"AU-ID({author_id})",  # Filtra per Author ID
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
                start += count
            else:
                print(f"Errore nella richiesta degli articoli: {response.status_code} - {response.text}")
                break
        except requests.RequestException as e:
            print(f"Errore nella richiesta: {e}")
            break

    return articles

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



def get_citing_articles( eid, api_key):
    """
    Recupera i DOI degli articoli che citano un articolo dato.
    
    Parametri:
        api_key (str): Chiave API Elsevier.
        eid (str): EID dell'articolo da analizzare.
    
    Ritorna:
        list: Lista di DOI degli articoli citanti.
    """
    base_url = "https://api.elsevier.com/content/search/scopus"
    start = 0
    step = 25

    citing_dois = []
    
    while True :
        params = {  "start" : start,
                    "count" : step, 
                    "apikey": api_key,
                    "query" : f"REF({eid})",
                    "view"  : "STANDARD" }

        response = requests.get( base_url, params=params )
        if ( response.status_code == 200 ) :
            data = response.json()
            entries = data.get("search-results", {}).get("entry", [])
            
            for entry in entries:
                res = entry.get("prism:doi", "N/A")
                if ( res != "N/A" ) :
                    citing_dois.append( res )
                else:
                    return citing_dois
            if not entries:
                return citing_dois
        else:
            return citing_dois
        start = start + step

    return citing_dois


def get_reference_count_from_eid( eid, api_key):
    """
    Ottiene il numero di riferimenti (references) in un articolo dato il suo EID.

    Parametri:
        api_key (str): La chiave API Elsevier valida.
        eid (str): L'EID dell'articolo.

    Ritorna:
        int: Numero di riferimenti, oppure -1 in caso di errore.
    """
    base_url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
    headers = {"X-ELS-APIKey": api_key}

    try:
        # Effettua la richiesta API
        response = requests.get(base_url, headers=headers)

        if response.status_code == 200:
            # Analizza il JSON della risposta
            data = response.json()
            reference_count = data.get("abstracts-retrieval-response", {}).get("coredata", {}).get("references-count", 0)

            # Restituisce il numero di riferimenti
            return int(reference_count)
        else:
            # Gestisce gli errori dell'API
            print(f"Errore API: {response.status_code} - {response.text}")
            return -1
    except requests.RequestException as e:
        # Gestisce le eccezioni durante la richiesta
        print(f"Errore durante la richiesta: {e}")
        return -1


def get_publication_year_using_crossref( doi ):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['message']['issued']['date-parts'][0][0]  # Extracts the year
        #return data['message']['published']['date-parts'][0][0]  # Extracts the year
    else:
        return "DOI not found or an error occurred."


def get_publication_year_using_scopus(doi, api_key):
    """
    Recupera l'anno di pubblicazione di un articolo dato il suo DOI usando l'API di Elsevier.

    Parameters:
        doi (str): Il DOI dell'articolo.
        api_key (str): La tua chiave API di Elsevier.

    Returns:
        str: L'anno di pubblicazione (YYYY), oppure None in caso di errore.
    """
    base_url = "https://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"  # Richiedi la risposta in formato JSON
    }
    params = {
        "query": f"DOI({doi})",
        "view": "COMPLETE"
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Solleva un'eccezione per errori HTTP

        data = response.json()
        entries = data.get("search-results", {}).get("entry", [])
        if entries:
            cover_date = entries[0].get("prism:coverDate")
            if cover_date:
                return int(cover_date[:4])  # Estrae i primi 4 caratteri (l'anno)
        return None

    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta API: {e}")
        return None


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

def get_authors_by_eid( eid, api_key ):
    """
    Retrieve the list of authors for a paper using its EID via the Scopus API.

    Parameters:
        eid (str): The Scopus EID of the paper.
        api_key (str): Your Elsevier API key.

    Returns:
        list: A list of author names or an error message.
    """
    base_url = "https://api.elsevier.com/content/abstract/eid/"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }

    response = requests.get(base_url + eid, headers=headers)

    if response.status_code == 200:
        data = response.json()
        try:
            authors = data["abstracts-retrieval-response"]["authors"]["author"]
            author_list = [author["ce:indexed-name"] for author in authors]
            return author_list
        except KeyError:
            return "No authors found in the response."
    else:
        return f"Error: {response.status_code}, {response.text}"

import requests

def get_article_year_by_eid( eid, api_key):
    """
    Retrieve the year of publication for a paper using its EID via the Scopus API.

    Parameters:
        eid (str): The Scopus EID of the paper.
        api_key (str): Your Elsevier API key.

    Returns:
        str: The year of publication or an error message.
    """
    base_url = "https://api.elsevier.com/content/abstract/eid/"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }

    response = requests.get( base_url + eid, headers=headers)

    if response.status_code == 200:
        data = response.json()
        try:
            year = data["abstracts-retrieval-response"]["coredata"]["prism:coverDate"].split("-")[0]
            return year
        except KeyError:
            return "Year of publication not found in the response."
    else:
        return f"Error: {response.status_code}, {response.text}"

import requests

def get_citing_articles_by_eid( eid, api_key):
    """
    Retrieve the EIDs of articles citing a paper using its EID via the Scopus API.

    Parameters:
        eid (str): The Scopus EID of the paper.
        api_key (str): Your Elsevier API key.

    Returns:
        list: A list of EIDs of citing articles or an error message.
    """
    base_url = "https://api.elsevier.com/content/abstract/eid/"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }

    response = requests.get(base_url + eid + "/citedby", headers=headers)

    if response.status_code == 200:
        data = response.json()
        try:
            citing_articles = data["abstracts-retrieval-response"]["citeInfoMatrix"]["citeInfoMatrixXML"]["citation"]["ref-info"]
            citing_eids = [article["scopus-id"] for article in citing_articles if "scopus-id" in article]
            return citing_eids
        except KeyError:
            return "No citing articles found in the response."
    else:
        return f"Error: {response.status_code}, {response.text}"

#########################################################
# Manages the citations for the current article and returns:
# - sum of reference scores
# - list of citing years
def manage_citing_articles( author_article_citing_dois, api_key) :

    author_article_num_ref = 0.0
    author_article_citing_years = []
    num_citing_dois = len( author_article_citing_dois )
    
    print(f"Running the {num_citing_dois} citation queries for this article")
    for k, c_doi in enumerate( author_article_citing_dois ):
        print( f"{k+1} - " , end=" " , flush=True )
        references = get_references_by_doi( c_doi )           
        author_article_num_ref = author_article_num_ref + 1/len( references )
        
        # citing_years = get_publication_year_using_crossref( c_doi )
        citing_year = get_publication_year_using_scopus( c_doi , api_key )
        author_article_citing_years.append( citing_year )
        print(f"{citing_year} || ", end=" " , flush=True )
        time.sleep(1)  # Sleep for some second, to avoid hitting the API too quickly
    print("\n")
    
    return author_article_num_ref, author_article_citing_years


#####################################################
# Gets a string that contains the words contained in the name and surname, and compose them considering that 
# - the words for name are all lowercase 
# - the words for surname are all uppercase 
def extract_surname_and_name( full_name ):
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

###########################################################
# Searches the name, surname and institution of the last author saved in the csv file 

def manage_last_author_articles( csv_file_path ):
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

    

#######################################################################
# If the author is already written in the article list, it returns True
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
            "name"               : articles["name"        ][k],
            "surname"            : articles["surname"     ][k],
            "institution"        : articles["institution" ][k],
            "author_id"          : articles["author_id"   ][k],
            "article_eid"        : articles["article_eid" ][k],
            "year"               : articles["year"        ][k],
            "num_aut"            : articles["num_aut"     ][k],
            "num_cit"            : articles["num_cit"     ][k],
            "article_refs"       : articles["article_refs"][k],
            "num_ref_in_citing"  : articles["num_ref_in_citing"][k],
            "citing_years"       : articles["citing_years"     ][k] } 
            for k in range( len( articles["name"] ) ) ] )


##############################################################
# Creates a list of unique authors, got from the articles list 
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
def CSV_file_setup( csv_file_path ):
    if not os.path.exists(csv_file_path):
        print(f"\n\nCSV file {csv_file_path} does not exist. It will be created")
        with open(csv_file_path, "w", encoding="utf-8", newline="") as file:
            pass

    if os.stat(csv_file_path).st_size == 0:
        print(f"\n\nCSV file {csv_file_path} hasn't the header. It will be written in the first row")
        with open(csv_file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, delimiter="|", fieldnames=["name", "surname", "institution", "author_id", "article_eid", "year", "num_aut", "num_cit", "article_refs", "num_ref_in_citing", "citing_years"])       
            writer.writeheader()    

    # Cleans the CSV file from special string characters
    answer = input (f"\n\nDo you want to clean the file named {csv_file_path}\nfrom wrong single and double quote characters? (Y/N): ")
    if answer.upper() == 'Y':
        csv_file_cleaning( csv_file_path )
        print(f"\n\nThe file {csv_file_path} was cleaned from wrong characters")        


############################################################
# Creates a list of authors from the XLS file, and adds the last author to it if it is not already present
def XLS_authors_list(xls_file_path, last_CSV_author_name, last_CSV_author_surname, last_CSV_author_institution):
    import pandas as pd

    if last_CSV_author_name is not None:
        XLS_authors = {
            "name": [last_CSV_author_name.lower()],
            "surname": [last_CSV_author_surname.lower()],
            "institution": [last_CSV_author_institution.lower()],
            "au_id": [""]
        }
    else:
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
