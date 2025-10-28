
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 19:21:41 2024

@author: Paolo Castellini
"""

import functions_revolver
import pandas as pd
import csv
import os
import platform
import time

###############################################################################################################
# Program flag and constant settings 
FLAG_INITIAL_CSV_CLEANING = False  # If True, it will ask if has to clean the CSV file from wrong single and double quote characters
FIRST_AUTHOR_TO_PROCESS   = 115    # First author to be processed. Set to 1 to process all the authors
MAX_NUM_OF_CITATIONS      = 100    # Maximum number of citations for an article to be processed. Articles with a higher number of citations will be skipped

AUTHOR_PAUSE_TIME       =   1 # Time in seconds to pause between two subsequent queries onan author author, to avoid exceeding the maximum number of requests per minute/hour/day
CITATION_PAUSE_TIME     =   2 # Time in seconds to pause between two subsequent queries on citations for the same article, to avoid exceeding the maximum number of requests per minute/hour/day
ARTICLE_PAUSE_TIME      =   2 # Time in seconds to pause between two subsequent queries on articles for the same author, to avoid exceeding the maximum number of requests per minute/hour/day

##############################################################################################################
# API Key settings
# API_KEY = "c81e40b973484fb83db5c697eadc3bea" # Chiave API Cast
# API_KEY = "18acfcf2e6f1ef665eec335c2fc40fcc" # Chiave API Forlano
# API_KEY = "10f7de16ece6898e37b7f9c6d6a68eb7" # Chiave API Caputo
# API_KEY = "a4be5d6403465914a622246057f086e0" # Chiave API Scocco 1
# API_KEY = "d1dd3948f277cd381a11337c51d72f67" # Chiave API Scocco 2

# To be used with revolver of API keys, to avoid exceeding the maximum number of requests per minute/hour/day

API_KEY_PAUSE_TIME      =  20 # Time in seconds to pause between the switch to the next api key use
API_KEY_ROLL_PAUSE_TIME = 400 # Time in seconds to pause between the switch to the first api key after a complete loop of all the available keys

MAX_KEY_LOOPS  = 3       # Maximum number of loops to check the API keys

API_KEYS = [ 
             "c81e40b973484fb83db5c697eadc3bea",  # Chiave API Cast
             "a4be5d6403465914a622246057f086e0",  # Chiave API Scocco 1
             "10f7de16ece6898e37b7f9c6d6a68eb7",  # Chiave API Caputo
             "18acfcf2e6f1ef665eec335c2fc40fcc",  # Chiave API Forlano 
             "d1dd3948f277cd381a11337c51d72f67" ] # Chiave API Scocco 2
"""
API_KEYS = [ 
             "c81e40b973484fb83db5c697eadc3bea"]  # Chiave API Cast 
"""

##############################################################################################################
# Author XLS and CSV articles file name settings

# reference_name = "misure"
# reference_name = "2_bioingegneria_Arnulfo-"
# reference_name = "1_bioingegneria_Accardo-Armonaite"
# reference_name = "3_bioingegneria_Vena-Veneroni"
REFERENCE_NAME = "EBMC"
xls_file_name = REFERENCE_NAME + ".xlsx" # Rows must be in order by column "Cognome e Nome" (Col. B) 
csv_file_name = REFERENCE_NAME + ".csv"
log_file_name = REFERENCE_NAME + "_log.txt"
skipped_author_file_name  = REFERENCE_NAME + "_skip-author.txt"
skipped_article_file_name = REFERENCE_NAME + "_skip-article.txt"

if platform.system() == "Windows":
    hostname = platform.node()
    if hostname == 'DESKTOP-K6PVP1F':  # Sostituisci con il nome reale del PC "Calypso"
        # base_dir_path = r"C:\Users\CMM\Desktop\20250327_Bibliometry\Dati"
        base_dir_path = r"F:\Bibliometry\bibliometry\Dati"
    elif hostname == 'Grifone': # Sostituisci con il nome reale del PC "Alberto"
        base_dir_path = r"F:\OneDrive - Università Politecnica delle Marche\Attivita\UnivPM\20250327_Bibliometry\Dati"
    else:
        # Imposta un percorso di default o lancia un errore se il computer non è riconosciuto
        raise ValueError(f"Computer non riconosciuto: '{hostname}'. Impossibile impostare base_dir_path.")
    data_dir_path = os.path.join(base_dir_path, REFERENCE_NAME)

else:
    # Qui puoi definire un percorso per altri sistemi operativi (es. Linux, macOS) o lanciare un errore
    raise NotImplementedError(f"Il sistema operativo '{platform.system()}' non è attualmente supportato.")

xls_file_path = os.path.join(data_dir_path, xls_file_name)
csv_file_path = os.path.join(data_dir_path, csv_file_name)
log_file_path = os.path.join(data_dir_path, log_file_name)
skipped_author_file_path  = os.path.join(data_dir_path, skipped_author_file_name)
skipped_article_file_path = os.path.join(data_dir_path, skipped_article_file_name)

print(f"\n\nFiles to be processed\n- CSV article data file name: {csv_file_path}\n- XLS authors file name: {xls_file_path}\n- LOG file name: {log_file_path}\n- SKIPPED AUTHORS file name: {skipped_author_file_path}\n- SKIPPED ARTICLES file name: {skipped_article_file_path}\n\n")

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

###################################################################################
# Sets up the log file with the time marker
functions_revolver.log_file_setup( log_file_path )

#############################
# Sets up the log file for the skipped authors 
functions_revolver.skipped_file_setup( skipped_author_file_path )

##########################################
# Sets up the CSV file 
# - creating it if it doesn't exist 
# - writing the header if it's empty
# - cleaning it from wrong characters (single and double quotes)
functions_revolver.CSV_file_setup( csv_file_path )

if FLAG_INITIAL_CSV_CLEANING: # Cleans the CSV file from special string characters
    answer = input (f"\n\nDo you want to clean the file named {csv_file_path}\nfrom wrong single and double quote characters? (Y/N): ")
    if answer.upper() == 'Y':
        functions_revolver.csv_file_cleaning( csv_file_path )
        print(f"\n\nThe file {csv_file_path} was cleaned from wrong characters")      

###########################################################
# Load all the authors XLS rows in a dictionary of list of strings, with keys called name, surname and institution 
# The first elements are the one previously deleted from the CSV file in the previous step
XLS_authors = functions_revolver.XLS_authors_list( xls_file_path ) # Load the authors from the XLS file

#############################################################
# Loads the CSV file in a dictionary of list of strings, with keys called name, surname and institution
# The first elements are the one previously deleted from the CSV file in the previous step
articles = functions_revolver.load_CSV_articles( csv_file_path )

##############################################################################################################
# Scopus search for each author by Surname Name and Institution of the author
print("Inizio ricerca su Scopus\n\n")

# Gets the API key from the list of keys, checking if it is valid
api_key_revolver = functions_revolver.get_next_API_key( api_key_revolver )

# Modifica per debug: il loop parte dall'autore in posizione 54 (indice 53)
for cont_author in range( FIRST_AUTHOR_TO_PROCESS, len( XLS_authors["name"] ) ):
 # for cont_author in range( 0, len( XLS_authors["name"] ) ):
    # Load the current author's data from the XLS dictionary
    name_XLS         = XLS_authors["name"       ][cont_author].lower()  # Lowercase the name to avoid problems with Scopus search            
    surname_XLS      = XLS_authors["surname"    ][cont_author].lower()  # Lowercase the surname to avoid problems with Scopus search      
    institution_XLS  = XLS_authors["institution"][cont_author].lower()  # Lowercase the institution to avoid problems with Scopus search 
    author_au_id_XLS        = XLS_authors["au_id"      ][cont_author].lower()  # Lowercase the au_id to avoid problems with Scopus search

    time.sleep( AUTHOR_PAUSE_TIME ) # Slows down the process to avoid exceeding the API request limit
    
    au_id_found_flag = True
    nsi_found_flag   = True
    if ( author_au_id_XLS is not None ) and ( author_au_id_XLS != "" ) : # If an Au_ID is found in XLS, it has the priority to search the author in Scopus 
        author_data_elements  = functions_revolver.search_author_with_au_id( author_au_id_XLS, api_key_revolver )     # Search for the author in Scopus, using the given Au_ID          
        author_search_results = author_data_elements.get( "search-results", {} ).get( "entry", [] )
      
        if ( author_search_results is None or len(author_search_results) == 0 ) : # If the author is not found using the au_id, try to search with name, surname and istitution
            author_data_elements  = functions_revolver.search_author_with_institution( name_XLS, surname_XLS, institution_XLS, api_key_revolver )     # Search for the author in Scopus, using name, surname and institution

            author_search_results = author_data_elements.get( "search-results", {} ).get( "entry", [] )
            au_id_found_flag = False
                
    else:
        author_data_elements  = functions_revolver.search_author_with_institution( name_XLS, surname_XLS, institution_XLS, api_key_revolver )

        author_search_results = author_data_elements.get( "search-results", {} ).get( "entry", [] )
        if ( author_search_results is None or len(author_search_results) == 0 ) :
            nsi_found_flag = False

    ################################################
    # nsi_flag refers to XLS Name Surname Institution search in Scopus
    # au_id_flag refers to XLS Au_ID search in Scopus
    if ( nsi_found_flag is False ) and ( au_id_found_flag is False ) :    
        text = f"This author will be skipped, since XLS record wasn't found in Scopus archive: surname = {surname_XLS}, name = {name_XLS}, affiliation = {institution_XLS}, id = {author_au_id_XLS}, so will be skipped\n"
        print( text )
        with open(log_file_path, "a", encoding="utf-8") as file:
            file.write( text )
        with open(skipped_author_file_path, "a", encoding="utf-8") as file:
            file.write( text )
        continue

    ###################################
    # Loop to print a row of author's data, one for each affiliation istitution  
    for entry in author_search_results : 
        surname_Scopus           = entry.get( 'preferred-name'     , {}).get( 'surname'         )
        name_Scopus              = entry.get( 'preferred-name'     , {}).get( 'given-name'      )
        affiliation_Scopus       = entry.get( 'affiliation-current', {}).get( 'affiliation-name')
        
        if au_id_found_flag :
            if surname_Scopus is None:
                surname_Scopus = surname_XLS.lower()      
            else:
                surname_Scopus = surname_Scopus.lower()         
            if name_Scopus is None:
                name_Scopus = name_XLS.lower()
            else:
                name_Scopus = name_Scopus.lower()
            if affiliation_Scopus is None:
                affiliation_Scopus = institution_XLS.lower()
            else:
                affiliation_Scopus = affiliation_Scopus.lower()
            
        text = "\n\n\n####################\n####################\n####################\n\n" + \
                f"Author n. {cont_author+1}/{len(XLS_authors['name'])}\n" + \
                f"XLS Name        : { name_XLS }\n" + \
                f"Scopus Name     : { name_Scopus }\n" + \
                f"XLS Surname     : { surname_XLS }\n" + \
                f"Scopus Surname  : { surname_Scopus }\n" + \
                f"XLS Institution    : { institution_XLS }\n" + \
                f"Scopus Institution : { affiliation_Scopus }\n" + \
                f"XLS Scopus ID      : { author_au_id_XLS }\n"   

        if ( nsi_found_flag is False ) and ( au_id_found_flag is False ) :    
            text = text + f"\nThis author will be skipped, since XLS record wasn't found in Scopus archive: surname = {surname_XLS}, name = {name_XLS}, affiliation = {institution_XLS}, id = {author_au_id_XLS}\n"
        
            with open(     log_file_path, "a", encoding="utf-8") as file:
                file.write( text )
            with open( skipped_author_file_path, "a", encoding="utf-8") as file:
                file.write( text )
            continue
                
        author_id_obj    = entry.get( 'dc:identifier'          )
        author_id_string = str( author_id_obj )
        author_id_Scopus = author_id_string[ 10: ]   # The id code is in the form 'AUTHOR_ID:58119182300'
        
        text = text + f"Scopus ID          : { author_id_Scopus }\n" + \
                      "\n####################\n####################\n####################\n\n"
        
        if not ( ( affiliation_Scopus in institution_XLS ) or ( institution_XLS in affiliation_Scopus ) or ( author_au_id_XLS == author_id_Scopus ) ) :
            text = text + f"\nThis author will be skipped, since the author's SCOPUS key data are different from the one in the XLS file\n"
            print( text)
            with open(    log_file_path, "a", encoding="utf-8") as file:
                file.write( text )
            with open(skipped_author_file_path, "a", encoding="utf-8") as file:
                file.write( text )
            continue
        else:
            text = text + f"\nThis author will be processed, since the author's SCOPUS key data are the same as the one in the XLS file.\n"
            print( text )
            with open(log_file_path, "a", encoding="utf-8") as file:
                file.write( text )
                
        author_articles_list = functions_revolver.get_author_articles( author_id_Scopus , api_key_revolver )            # Gets the list of author articles
        
        message = f"\nThis author has {len(author_articles_list)} articles with the XLS institution: {institution_XLS} / Scopus institution: {affiliation_Scopus}\n"
        print( message )
        with open(log_file_path, "a", encoding="utf-8") as file:
            file.write( message )
            
        articles_data_list = []        
        for cont_article, article in enumerate( author_articles_list ):       

            article_data = list( article.values() )  
            
            author_article_title    = article_data[0]
            article_num_aut  = article_data[1]
            article_num_cit  = article_data[2]
            article_doi      = article_data[3]
            article_eid      = article_data[4]

            message = f"\n\n##############\n" # message = f"\n\n##############\nScopus Author: {name_Scopus} {surname_Scopus} - Scopus affiliation institution: {affiliation_Scopus}\n"
            message = message + f"Author n. {cont_author+1}/{len(XLS_authors['name'])}\nArticle n. {cont_article+1}/{len(author_articles_list)} - Title: {author_article_title}\n"
            print( message)
            with open(log_file_path, "a", encoding="utf-8") as file:
                file.write( message )
                    
            # Searches the article in the CSV file, to verify 
            # - if it is already found
            #       - for this author -> skip the article 
            #       - for another author -> write it for this author
            # - if it is not found in the CSV file -> write it for this author
            # This is done to avoid 
            # - reduce the queries with Scopus API
            # - writing the same article for the same author multiple times in the CSV file
           
            found_article_and_author_flag, article_data = functions_revolver.written_article_in_CSV_Scopus( articles, article_eid, author_id_Scopus )        
            message =           f"XLS Author Data     - Name: {name_XLS} , Surname: {surname_XLS} , Institution: {institution_XLS}\n"
            message = message + f"Scopus Author Data  - Name: {name_Scopus    } , Surname: {surname_Scopus    } , Affiliation: {affiliation_Scopus    }, Scopus ID: {author_id_Scopus}\n"                
            message = message + f"Scopus Article Data - N. of co-authors  : {article_num_aut}, N. of citations: {article_num_cit}\n"
            message = message + f"Article DOI: {article_doi} , Article EID: {article_eid}\n"

            if found_article_and_author_flag :
                message = message + "This article has already been processed and written in the CSV file for this author, so it will be skipped\n"
                print( message)
                with open( log_file_path, "a", encoding="utf-8" ) as file:
                    file.write( message )
                continue
            else:

                if article_num_cit > MAX_NUM_OF_CITATIONS:
                    message = message + f"This article will be skipped, since it has {article_num_cit} citations, higher than the maximum number of citations allowed ({MAX_NUM_OF_CITATIONS})\n"
                    print( message)
                    with open(    log_file_path, "a", encoding="utf-8") as file:
                        file.write( message )
                    with open(skipped_author_file_path, "a", encoding="utf-8") as file:
                        file.write( message )
                        
                    text = f"{name_XLS}|{surname_XLS}|{institution_XLS}|{author_id_Scopus}|{article_doi}|{article_eid}|{article_num_cit}\n"
                    with open(skipped_article_file_path, "a", encoding="utf-8") as file:
                        file.write( text )                    
                    continue  

                message = message + "This article has never been processed and written in the CSV file: the query will be done and these data will be written for this author\n"
                print( message )
                with open(log_file_path, "a", encoding="utf-8") as file:
                    file.write( message )
                                
                # author_article_authors = functions_revolver.get_authors_by_eid( article_eid, api_key_revolver )
                # article_num_aut = len( author_article_authors )  

                article_year = functions_revolver.get_article_year_by_eid( article_eid, api_key_revolver )    
                                    
                article_references = functions_revolver.get_references_by_doi( article_doi ) # Gets the list of reference articles
                author_article_num_references = len( article_references )          

                # Gets the dois codes for the citing articles of the selected article
                # then manages the citing articles to get the number of references in the citing articles and the years of the citing articles 
                author_article_citing_dois = functions_revolver.get_citing_articles( article_eid , api_key_revolver )
                author_article_citing_years, citing_articles_ref_counts = functions_revolver.get_scopus_data_for_citing_dois(author_article_citing_dois, api_key_revolver)
                
                # Calcola il punteggio basato sul numero di referenze ottenute
                author_article_num_ref = 0.0
                for ref_count in citing_articles_ref_counts:
                    if ref_count > 0:
                        author_article_num_ref = ( 1 / ref_count ) + author_article_num_ref
            
            current_article_data = {"name":         name_Scopus ,
                                    "surname":      surname_Scopus, 
                                    "institution":  functions_revolver.clean_field( affiliation_Scopus ),
                                    "author_id":    author_id_Scopus,
                                    "article_eid":  article_eid,
                                    "year":         article_year,
                                    "num_aut":      article_num_aut, 
                                    "num_cit":      article_num_cit, 
                                    "article_refs": author_article_num_references,
                                    "num_ref_in_citing": author_article_num_ref  ,
                                    "citing_years": functions_revolver.clean_field ( author_article_citing_years ) }
                       
            with open(csv_file_path, "a", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, delimiter="|", fieldnames=["name", "surname", "institution", "author_id", "article_eid", "year", "num_aut", "num_cit", "article_refs", "num_ref_in_citing", "citing_years"])       
                writer.writerows( [current_article_data] )
            
            articles_data_list.append( current_article_data )
            articles.append( current_article_data )
            
            with open(log_file_path, "a", encoding="utf-8") as file:
                file.write( f"Number of citations: {article_num_cit}\n")
                file.write( f"Number of references: {author_article_num_references}\n")
                file.write( f"Citing years: {author_article_citing_years}\n")

            time.sleep( ARTICLE_PAUSE_TIME ) # Rallenta il processo per evitare di superare il limite di richieste API

        num_articles = len( articles_data_list )
        message = f"\n\nFor this author were found {num_articles} new articles with the XLS institution {institution_XLS} / Scopus institution {affiliation_Scopus}\n"
        for cont_article in range (num_articles):
            message = message + f"Art. {cont_article+1}/ {num_articles} ) {articles_data_list[cont_article]}\n"
        print( message )
        with open(log_file_path, "a", encoding="utf-8") as file:
            file.write( message )

print(f"\n\nEnd of the search for author's articles in Scopus\n")
