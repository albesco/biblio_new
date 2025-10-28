# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 19:21:41 2024.
Modified on Fri Apr 11 12:01:39 2025 # <-- Added the modification date

@author: Paolo Castellini
"""

import functions 
import pandas as pd # Importato ma non usato nel frammento, potrebbe essere in functions
import csv
import os
import platform
import time

##############################################################################################################
# API Key settings
API_KEY = "c81e40b973484fb83db5c697eadc3bea" # Cast API Key
# API_KEY = "18acfcf2e6f1ef665eec335c2fc40fcc" # Forlano API Key
# API_KEY="10f7de16ece6898e37b7f9c6d6a68eb7" # Caputo API Key
# API_KEY="a4be5d6403465914a622246057f086e0" # Scocco 1 API Key
# API_KEY="d1dd3948f277cd381a11337c51d72f67" # Scocco 2 API Key

##############################################################################################################
# Author XLS and CSV articles file name settings
reference_name = "misure"
xls_file_name = reference_name + ".xlsx"
csv_file_name = reference_name + ".csv"
log_file_name = reference_name + "_log.txt"
skipped_file_name = reference_name + "_skip.txt"

if platform.system() == "Windows":
    base_dir_path = r"C:\Users\CMM\Desktop\20250327_Bibliometry\Dati"
    # base_dir_path = r"F:\Alberto\Attivita\UnivPM\20250327_Bibliometry\Dati"
else:
    # Assume a default path for other systems if necessary
    base_dir_path = os.path.expanduser("~/Documents/Bibliometry/Dati") # Example for Linux/MacOS
    # Create the directory if it does not exist
    os.makedirs(base_dir_path, exist_ok=True)
    # base_dir_path = "/home/aisha/Documents/Cast/Test_sam2-main/notebooks/videos" # Old commented path

xls_file_path = os.path.join( base_dir_path, xls_file_name )
csv_file_path = os.path.join( base_dir_path, csv_file_name )
log_file_path = os.path.join( base_dir_path, log_file_name )
skipped_file_path = os.path.join( base_dir_path, skipped_file_name )


print(f"\n\nFiles to be processed\n- CSV article data file name: {csv_file_path}\n- XLS authors file name: {xls_file_path}\n- LOG file name: {log_file_path}\n- Skipped authors file: {skipped_file_path}")

###################################################################################
# Sets up the log file with the time marker
functions.log_file_setup( log_file_path )

#############################
# Sets up the log file for the skipped authors
functions.skipped_file_setup( skipped_file_path )

##########################################
# Sets up the CSV file
# - creating it if it doesn't exist
# - writing the header if it's empty
# - cleaning it from wrong characters (single and double quotes)
# NOTE: It is assumed that the cleaning request has been removed INSIDE this function.
functions.CSV_file_setup( csv_file_path )

#####################################################
# --- REMOVED ---
# Management of the last author in the CSV (user request removed)
# last_CSV_author_name , last_CSV_author_surname, last_CSV_author_institution = functions.manage_last_author_articles( csv_file_path )
###########################################################

# Load all the authors XLS rows in a dictionary of list of strings, with keys called name, surname and institution
# The call has been modified to no longer use the details of the last CSV author
XLS_authors = functions.XLS_authors_list( xls_file_path ) # Load the authors from the XLS file 


#############################################################
# Loads the CSV file in a dictionary of list of strings, with keys called name, surname and institution
# This is used to check the articles already written
articles = functions.load_CSV_articles(csv_file_path)

##############################################################################################################
# Scopus search for each author by Surname, Name and Institution of the author
print("Inizio ricerca su Scopus\n\n")

MAX_RETRIES = 5 # Numero massimo di tentativi consecutivi per autore

for k in range( 0, len( XLS_authors["name"] ) ):
    # Load the current author's data from the XLS dictionary
    author_name         = XLS_authors["name"       ][k]
    author_surname      = XLS_authors["surname"    ][k]
    author_institution  = XLS_authors["institution"][k]

    retry_count = 0
    author_processed_successfully = False

    # Retry loop for the single author
    while retry_count < MAX_RETRIES and not author_processed_successfully:
        try:
            print(f"\n--- Processing Author {k+1}/{len(XLS_authors['name'])}: {author_name} {author_surname} ({author_institution}) --- Attempt {retry_count + 1}/{MAX_RETRIES} ---")
            with open(log_file_path, "a", encoding="utf-8") as file:
                file.write(f"\n\n--- Processing Author {k+1}/{len(XLS_authors['name'])}: {author_name} {author_surname} ({author_institution}) --- Attempt {retry_count + 1}/{MAX_RETRIES} ---\n")

            # --- START TRY BLOCK FOR AUTHOR PROCESSING ---

            # Check if the author is already in the CSV file (logica commentata originale mantenuta commentata)
            # if ( functions.is_written_author( author_surname, author_name, author_institution, articles_authors_unique ) ) :
            #     print("\n\nThe following author is skipped: the search has been done and data are already written in the CSV file of articles")
            #     print(f"Name: {author_name}\nSurname: {author_surname}\nInstitution: {author_institution}\n")
            #     author_processed_successfully = True # Consideriamo successo se era già stato processato
            #     continue # Esce dal while, va al prossimo autore
            
            time.sleep(3) # Short pause before author search
            # Potenziale punto di eccezione 1
            author_data_elements = functions.search_author_with_institution( author_name, author_surname, author_institution, API_KEY )

            author_search_results = author_data_elements.get( "search-results", {} ).get( "entry", [] )

            if not author_search_results:
                 print(f"No results found for author {author_name} {author_surname} with institution {author_institution}. Skipping.")
                 with open(log_file_path, "a", encoding="utf-8") as file:
                     file.write(f"No results found for author {author_name} {author_surname} with institution {author_institution}. Skipping.\n")
                 with open(skipped_file_path, "a", encoding="utf-8") as file:
                     file.write("\n\n####################\n")
                     file.write( "\nSKIPPED AUTHOR - NO SCOPUS RESULTS FOUND\n\n")
                     file.write(f"Name         : { author_name }\n")
                     file.write(f"Surname      : { author_surname }\n")
                     file.write(f"Institution  : { author_institution }\n")
                     file.write("####################\n") 
                 author_processed_successfully = True # It is not an API error, the author is not there, we consider it "processed"
                 continue # Exits the while, goes to the next author in the main for loop


            author_processed_in_this_attempt = False # Flag to track if we have processed at least one record for this author
            
            ###################################
            # Loop sui risultati della ricerca per l'autore (potrebbero esserci più ID per lo stesso nome/istituzione)
            for entry in author_search_results :
                surname       = entry.get( 'preferred-name'   , {}).get( 'surname'        )
                name          = entry.get( 'preferred-name'   , {}).get( 'given-name'     )
                affiliation   = entry.get( 'affiliation-current', {}).get( 'affiliation-name')

                if surname is None:
                    # This can happen if the entry is not valid, we move on to the next entry if there is one
                    print("Skipping an invalid author entry (no surname).")
                    with open(log_file_path, "a", encoding="utf-8") as file:
                        file.write("Skipping an invalid author entry (no surname).\n")
                    continue # Go to the next entry in the 'for entry in...' loop

                # Normalize the fields for comparison
                surname = surname.lower() 
                name = name.lower()
                affiliation = affiliation.lower() if affiliation else "" # Gestisce affiliation mancante
                author_institution_lower = author_institution.lower() if author_institution else ""

                author_id_obj    = entry.get( 'dc:identifier'        )
                if not author_id_obj or not str(author_id_obj).startswith("AUTHOR_ID:"):
                     print(f"Skipping entry for {name} {surname} due to missing or invalid Scopus ID: {author_id_obj}")
                     with open(log_file_path, "a", encoding="utf-8") as file:
                         file.write(f"Skipping entry for {name} {surname} due to missing or invalid Scopus ID: {author_id_obj}\n")
                     continue # Go to the next entry

                author_id_string = str( author_id_obj )
                author_id = author_id_string[ 10: ] # L'ID è nella forma 'AUTHOR_ID:xxxxxxx'

                print("\n\n\n####################\n")
                print( "NEXT AUTHOR QUERY RESULT")
                print(f"Name         : { name }")
                print(f"Surname      : { surname }")
                print(f"Institution  : { affiliation }")
                print(f"Scopus ID    : { author_id }\n")

                with open(log_file_path, "a", encoding="utf-8") as file:
                    file.write( "\n\n\n####################\n\n")
                    file.write( "NEXT AUTHOR QUERY RESULT\n\n")
                    file.write(f"Name         : { name }\n")
                    file.write(f"Surname      : { surname }\n")
                    file.write(f"Institution  : { affiliation }\n")
                    file.write(f"Scopus ID    : { author_id }\n\n")

                # Affiliation comparison (more robust: checks if one contains the other)
                if not ( ( affiliation in author_institution_lower ) or ( author_institution_lower in affiliation ) ) :
                    print( f"Affiliation mismatch: Scopus='{affiliation}', XLS='{author_institution_lower}'. Skipping this Scopus ID.")
                    with open(log_file_path, "a", encoding="utf-8") as file:
                        file.write( f"Affiliation mismatch: Scopus='{affiliation}', XLS='{author_institution_lower}'. Skipping this Scopus ID.\n")
                    # Do not add to skipped_file here, the XLS author may match another entry
                    continue # Go to the next entry/ID for the same XLS author
                else:
                    print( f"Affiliation match: Scopus='{affiliation}', XLS='{author_institution_lower}'. Processing articles for this Scopus ID.")
                    with open(log_file_path, "a", encoding="utf-8") as file:
                        file.write(f"Affiliation match: Scopus='{affiliation}', XLS='{author_institution_lower}'. Processing articles for this Scopus ID.\n")

                # If the affiliation matches, proceed with this Author ID
                author_processed_in_this_attempt = True # We have found a valid record for the author

                # Potenziale punto di eccezione 2
                author_articles = functions.get_author_articles( author_id , API_KEY )

                articles_data_for_this_id = [] # Lista per gli articoli trovati con questo ID Scopus specifico
                print(f"Author ID {author_id} has {len(author_articles)} articles.")
                with open(log_file_path, "a", encoding="utf-8") as file:
                    file.write(f"Author ID {author_id} has {len(author_articles)} articles.\n")

                for idx, author_article in enumerate( author_articles ): 

                    # Extract the basic data of the article
                    # We assume that the order is: title, num_aut(to be updated), num_cit, doi, eid
                    # È più sicuro accedere tramite chiave se `author_article` è un dizionario
                    if isinstance(author_article, dict):
                        author_article_title = author_article.get('dc:title', 'Title not found')
                        # author_article_num_aut = author_article.get('num_authors', 0) # Verrà ricalcolato
                        author_article_num_cit = author_article.get('citedby-count', 0)
                        author_article_doi     = author_article.get('prism:doi')
                        author_article_eid     = author_article.get('eid')
                    else:
                         # Se non è un dizionario, prova con l'accesso posizionale originale (meno sicuro)
                         try:
                            author_article_elements = list( author_article.values() )
                            author_article_title   = author_article_elements[0]
                            # author_article_num_aut = author_article_elements[1] # Verrà ricalcolato
                            author_article_num_cit = author_article_elements[2]
                            author_article_doi     = author_article_elements[3]
                            author_article_eid     = author_article_elements[4]
                         except (IndexError, AttributeError):
                             print(f"Skipping article {idx+1} due to unexpected format: {author_article}")
                             with open(log_file_path, "a", encoding="utf-8") as file:
                                 file.write(f"Skipping article {idx+1} due to unexpected format: {author_article}\n")
                             continue # Skip this article


                    if not author_article_eid:
                        print(f"Skipping article {idx+1} (Title: {author_article_title[:50]}...) due to missing EID.")
                        with open(log_file_path, "a", encoding="utf-8") as file:
                            file.write(f"Skipping article {idx+1} (Title: {author_article_title[:50]}...) due to missing EID.\n")
                        continue # Salta questo articolo, EID è fondamentale
                    
                    print(f"\n\n##############\nProcessing Author: {author_name} {author_surname} - Inst: {author_institution}\nArticle {idx+1}/{len(author_articles)} - EID: {author_article_eid} - Title: {author_article_title[:60]}...")
                    with open(log_file_path, "a", encoding="utf-8") as file:
                       file.write(f"\n\n##############\nProcessing Author: {author_name} {author_surname} - Inst: {author_institution}\nArticle {idx+1}/{len(author_articles)} - EID: {author_article_eid} - Title: {author_article_title[:60]}...\n") 

                    # Controlla se l'articolo è già nel CSV caricato
                    if functions.written_article_in_CSV( articles, author_article_eid ) :
                        print("Article already in CSV. Skipping.")
                        with open(log_file_path, "a", encoding="utf-8") as file:
                           file.write("Article already in CSV. Skipping.\n")
                        continue # Salta questo articolo
                    
                    # We introduce pauses *before* the subsequent API calls
                    time.sleep(10) # Pause before API calls for the article
                    
                    # Potenziale punto di eccezione 3
                    author_article_authors = functions.get_authors_by_eid( author_article_eid, API_KEY )
                    author_article_num_aut = len( author_article_authors )

                    # Potenziale punto di eccezione 4 (se DOI esiste)
                    author_article_num_references = 0
                    if author_article_doi:
                        article_references = functions.get_references_by_doi( author_article_doi )
                        author_article_num_references = len( article_references )
                    else:
                        print("DOI not found for this article, cannot get references.")
                        with open(log_file_path, "a", encoding="utf-8") as file:
                            file.write("DOI not found for this article, cannot get references.\n")
                    

                    # Potenziale punto di eccezione 5
                    author_article_year = functions.get_article_year_by_eid( author_article_eid, API_KEY )

                    # Potenziale punto di eccezione 6 & 7
                    author_article_num_ref = 0
                    author_article_citing_years = ""
                    try:
                        author_article_citing_dois = functions.get_citing_articles( author_article_eid , API_KEY )
                        author_article_num_ref , author_article_citing_years = functions.manage_citing_articles( author_article_citing_dois)
                    except Exception as cite_e:
                        print(f"Warning: Could not process citing articles for EID {author_article_eid}: {cite_e}")
                        with open(log_file_path, "a", encoding="utf-8") as file:
                            file.write(f"Warning: Could not process citing articles for EID {author_article_eid}: {cite_e}\n")
                        # Continua comunque, ma con valori di default per i dati delle citazioni
                        author_article_num_ref = 0
                        author_article_citing_years = "ErrorProcessing"
                    
                    
                    # Prepara i dati per il CSV
                    current_article_data = {"name":         author_name ,
                                            "surname":      author_surname,
                                            "institution":  functions.clean_field( author_institution ),
                                            "author_id":    author_id,
                                            "article_eid":  author_article_eid,
                                            "year":         author_article_year,
                                            "num_aut":      author_article_num_aut,
                                            "num_cit":      author_article_num_cit,
                                            "article_refs": author_article_num_references,
                                            "num_ref_in_citing": author_article_num_ref,
                                            "citing_years": functions.clean_field( author_article_citing_years )
                                            }
                    
                    # Write to the CSV file IMMEDIATELY to save progress
                    with open(csv_file_path, "a", encoding="utf-8", newline="") as file:
                        writer = csv.DictWriter(file, delimiter="|", fieldnames=["name", "surname", "institution", "author_id", "article_eid", "year", "num_aut", "num_cit", "article_refs", "num_ref_in_citing", "citing_years"])
                        # Writes the header only if the file is empty (managed by CSV_file_setup or DictWriter)
                        # file.seek(0, os.SEEK_END) # Go to the end
                        # if file.tell() == 0: # Check if it is empty
                        #     writer.writeheader() # Scrive l'header se necessario (ma dovrebbe farlo CSV_file_setup)
                        writer.writerow( current_article_data )

                    articles_data_for_this_id.append( current_article_data )
                    articles.append( current_article_data ) # Aggiorna anche la lista in memoria

                    with open(log_file_path, "a", encoding="utf-8") as file:
                        file.write( f"Data saved:\n")
                        file.write( f"  Num Authors: {author_article_num_aut}\n")
                        file.write( f"  Num Citations: {author_article_num_cit}\n")
                        file.write( f"  Num References: {author_article_num_references}\n")
                        file.write( f"  Citing Years: {author_article_citing_years}\n")
                        file.write( f"  Num Refs in Citing: {author_article_num_ref}\n")

                    time.sleep(5) # Additional pause between articles to reduce API load


                # Print summary for this specific Scopus Author ID
                num_articles_saved_this_id = len(articles_data_for_this_id)
                print(f"\nSummary for Scopus ID {author_id}: Saved {num_articles_saved_this_id} new articles.")
                with open(log_file_path, "a", encoding="utf-8") as file:
                   file.write(f"\nSummary for Scopus ID {author_id}: Saved {num_articles_saved_this_id} new articles.\n")

            # End of the `for entry in author_search_results:` loop

            if not author_processed_in_this_attempt and author_search_results:
                # If there were results but none matched the institution or were valid
                print(f"No matching/valid Scopus records found for {author_name} {author_surname} at {author_institution} among the search results.")
                with open(log_file_path, "a", encoding="utf-8") as file:
                   file.write(f"No matching/valid Scopus records found for {author_name} {author_surname} at {author_institution} among the search results.\n")
                # We don't add it to the skipped here, because the initial search gave results
                # Potrebbe essere un problema di dati nell'XLS o in Scopus

            # Se siamo arrivati qui senza eccezioni, l'autore è stato processato con successo
            author_processed_successfully = True
            if retry_count > 0:
                print(f"Author {author_name} {author_surname} processed successfully on attempt {retry_count + 1}.")
                with open(log_file_path, "a", encoding="utf-8") as file:
                    file.write(f"Author {author_name} {author_surname} processed successfully on attempt {retry_count + 1}.\n")

            # --- END TRY BLOCK ---

        except Exception as e:
            retry_count += 1
            print(f"\n!!! EXCEPTION occurred processing author: {author_name} {author_surname} ({author_institution})")
            print(f"Error type: {type(e).__name__}, Message: {e}")
            # Logga l'errore
            with open(log_file_path, "a", encoding="utf-8") as log_file:
               log_file.write(f"\n\n!!! EXCEPTION on Author: {author_name} {author_surname} ({author_institution})\n") 
               log_file.write(f"Attempt {retry_count}/{MAX_RETRIES}. Error: {type(e).__name__}: {e}\n")
               import traceback
               log_file.write("Traceback:\n")
               traceback.print_exc(file=log_file) # Print the traceback in the log
               log_file.write("\n") 


            if retry_count < MAX_RETRIES:
                wait_time = 300 # 5 minuti
                print(f"Attempt {retry_count}/{MAX_RETRIES}. Waiting {wait_time // 60} minutes before retrying...")
                with open(log_file_path, "a", encoding="utf-8") as log_file:
                   log_file.write(f"Waiting {wait_time} seconds before retry...\n")
                time.sleep(wait_time)
            else:
                print(f"Maximum retries ({MAX_RETRIES}) reached for author {author_name} {author_surname}. Skipping this author.")
                # Logga il fallimento finale e aggiungi allo skipped file
                with open(log_file_path, "a", encoding="utf-8") as log_file:
                   log_file.write(f"Maximum retries ({MAX_RETRIES}) reached. Skipping author {author_name} {author_surname}.\n")
                with open(skipped_file_path, "a", encoding="utf-8") as skip_file:
                   skip_file.write("\n\n####################\n")
                   skip_file.write(f"\nSKIPPED AUTHOR DUE TO REPEATED ERRORS (after {MAX_RETRIES} retries)\n")
                   skip_file.write(f"Name         : {author_name}\n")
                   skip_file.write(f"Surname      : {author_surname}\n")
                   skip_file.write(f"Institution  : {author_institution}\n")
                   skip_file.write(f"Last Error   : {type(e).__name__}: {e}\n")
                   skip_file.write("####################\n")
                # The while loop will terminate because retry_count >= MAX_RETRIES

    # End of the retry while loop for the current author
    # The main for loop will move on to the next author (k+1)

print(f"\n\nEnd of the search for author's articles in Scopus\n")
