
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 19:21:41 2024

@author: Paolo Castellini
"""

import functions
import pandas as pd
import csv
import os
import platform
import time

##############################################################################################################
# API Key settings
API_KEY = "c81e40b973484fb83db5c697eadc3bea" # Chiave API Cast

# API_KEY = "18acfcf2e6f1ef665eec335c2fc40fcc" # Chiave API Forlano

# API_KEY="10f7de16ece6898e37b7f9c6d6a68eb7" # Chiave API Caputo

# API_KEY="a4be5d6403465914a622246057f086e0" # Chiave API Scocco 1

# API_KEY="d1dd3948f277cd381a11337c51d72f67" # Chiave API Scocco 2

##############################################################################################################
# Author XLS and CSV articles file name settings

# reference_name = "misure"
# reference_name = "2_bioingegneria_Arnulfo-"
# reference_name = "1_bioingegneria_Accardo-Armonaite"
# reference_name = "3_bioingegneria_Vena-Veneroni"
reference_name = "elettronica_informazione"
xls_file_name = reference_name + ".xlsx" # Rows must be in order by column "Cognome e Nome" (Col. B) 
csv_file_name = reference_name + ".csv"
log_file_name = reference_name + "_log.txt"
skipped_file_name = reference_name + "_skip.txt"

if platform.system() == "Windows":
    base_dir_path = r"C:\Users\CMM\Desktop\20250327_Bibliometry\Dati\Elettronica_Informazione"
    # base_dir_path = r"F:\Alberto\Attivita\UnivPM\20250327_Bibliometry\Dati\Elettronica_Informazione"

xls_file_path = os.path.join( base_dir_path, xls_file_name )
csv_file_path = os.path.join( base_dir_path, csv_file_name )
log_file_path = os.path.join( base_dir_path, log_file_name )
skipped_file_path = os.path.join( base_dir_path, skipped_file_name )

print(f"\n\nFiles to be processed\n- CSV article data file name: {csv_file_path}\n- XLS authors file name: {xls_file_path}\n- LOG file name: {log_file_path}")

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
functions.CSV_file_setup( csv_file_path )

#####################################################
# Manages the problem of the last author in the CSV file, because there could be a partial download.
# The user can choose to delete the last author's data, or stop the execution
# If chooses to proceed and delete, the author's name, surname and institution are given back from the function  
last_CSV_author_name , last_CSV_author_surname, last_CSV_author_institution = functions.manage_last_author_articles( csv_file_path )

###########################################################
# Load all the authors XLS rows in a dictionary of list of strings, with keys called name, surname and institution 
# The first elements are the one previously deleted from the CSV file in the previous step
XLS_authors = functions.XLS_authors_list( xls_file_path, last_CSV_author_name , last_CSV_author_surname, last_CSV_author_institution ) # Load the authors from the XLS file

#############################################################
# Loads the CSV file in a dictionary of list of strings, with keys called name, surname and institution
# The first elements are the one previously deleted from the CSV file in the previous step
articles = functions.load_CSV_articles(csv_file_path)

##############################################################################################################
# Scopus search for each author by Surname Name and Institution of the author
print("Inizio ricerca su Scopus\n\n")

for k in range( 0, len( XLS_authors["name"] ) ):
    # Load the current author's data from the XLS dictionary
    author_name         = XLS_authors["name"       ][k].lower()  # Lowercase the name to avoid problems with Scopus search            
    author_surname      = XLS_authors["surname"    ][k].lower()  # Lowercase the surname to avoid problems with Scopus search      
    author_institution  = XLS_authors["institution"][k].lower()  # Lowercase the institution to avoid problems with Scopus search 
    author_au_id        = XLS_authors["au_id"      ][k].lower()  # Lowercase the au_id to avoid problems with Scopus search

    time.sleep(1)
    
    au_id_found_flag = True
    nsi_found_flag   = True
    if ( author_au_id is not None ) and ( author_au_id != "" ) :
        author_data_elements  = functions.search_author_with_au_id( author_au_id, API_KEY )     # Search for the author in Scopus, using the given Au_ID
        author_search_results = author_data_elements.get( "search-results", {} ).get( "entry", [] )
      
        if ( author_search_results is None or len(author_search_results) == 0 ) : # If the author is not found using the au_id
            author_data_elements  = functions.search_author_with_institution( author_name, author_surname, author_institution, API_KEY )     # Search for the author in Scopus, using name, surname and institution
            author_search_results = author_data_elements.get( "search-results", {} ).get( "entry", [] )
            au_id_found_flag = False
    else:
        author_data_elements  = functions.search_author_with_institution( author_name, author_surname, author_institution, API_KEY )
        author_search_results = author_data_elements.get( "search-results", {} ).get( "entry", [] )
        if ( author_search_results is None or len(author_search_results) == 0 ) :
            nsi_found_flag = False
    
    if ( nsi_found_flag is False ) and ( au_id_found_flag is False ) :    
        print( f"This author will be skipped, since XLS record wasn't found in Scopus archive: surname = {author_surname}, name = {author_name}, affiliation = {author_institution}, id = {author_au_id}, so will be skipped\n")
        with open(log_file_path, "a", encoding="utf-8") as file:
            file.write( "\n\n\n####################\n\n")
            file.write(f"This author will be skipped, since XLS record wasn't found in Scopus archive: surname = {author_surname}, name = {author_name}, affiliation = {author_institution}, id = {author_au_id}, so will be skipped\n")   
        with open(skipped_file_path, "a", encoding="utf-8") as file:
            file.write( "\n\n\n####################\n\n")
            file.write(f"This author will be skipped, since XLS record wasn't found in Scopus archive: surname = {author_surname}, name = {author_name}, affiliation = {author_institution}, id = {author_au_id}, so will be skipped\n")   
        continue

    ###################################
    # Loop to print a row of author's data, one for each affiliation istitution  
    for entry in author_search_results : 
        surname           = entry.get( 'preferred-name'     , {}).get( 'surname'         )
        name              = entry.get( 'preferred-name'     , {}).get( 'given-name'      )
        affiliation       = entry.get( 'affiliation-current', {}).get( 'affiliation-name')
        
        if au_id_found_flag :
            if surname is None:
                surname = author_surname.lower()      
            else:
                surname = surname.lower()         
            if name is None:
                name = author_name.lower()
            else:
                name = name.lower()
            if affiliation is None:
                affiliation = author_institution.lower()
            else:
                affiliation = affiliation.lower()

            
        text = "\n\n\n####################\n\n" + \
                f"XLS Name        : { author_name }\n" + \
                f"Scopus Name     : { name }\n" + \
                f"XLS Surname     : { author_surname }\n" + \
                f"Scopus Surname  : { surname }\n" + \
                f"XLS Institution    : { author_institution }\n" + \
                f"Scopus Institution : { affiliation }\n" + \
                f"XLS Scopus ID      : { author_au_id }\n"

        if ( nsi_found_flag is False ) and ( au_id_found_flag is False ) :    
            text = text + f"\nThis author will be skipped, since XLS record wasn't found in Scopus archive: surname = {author_surname}, name = {author_name}, affiliation = {author_institution}, id = {author_au_id}, so will be skipped\n"
        
            with open(     log_file_path, "a", encoding="utf-8") as file:
                file.write( text )
            with open( skipped_file_path, "a", encoding="utf-8") as file:
                file.write( text )
            continue
 
                
        author_id_obj     = entry.get( 'dc:identifier'          )
        author_id_string = str( author_id_obj )
        author_id = author_id_string[ 10: ]   # The id code is in the form 'AUTHOR_ID:58119182300'
        
        text = text + f"Scopus ID          : { author_id }\n"
        
        # with open(log_file_path, "a", encoding="utf-8") as file:
          #   file.write( f"Scopus ID          : { author_id }\n" ) 
        
        if not ( ( affiliation in author_institution ) or ( author_institution in affiliation ) ) :
            print( text + f"\nThis author's record has a different affiliation institution [{affiliation}] from the one [{author_institution}] in the XLS file. from the one searched in the XLS file, so will be skipped\n")
            with open(log_file_path, "a", encoding="utf-8") as file:
                file.write( text + f"\nThis author's record has a different affiliation institution [{affiliation}] from the one [{author_institution}] in the XLS file. from the one searched in the XLS file, so will be skipped\n")
            with open(skipped_file_path, "a", encoding="utf-8") as file:
                file.write( text + f"\nThis author's record has a different affiliation institution [{affiliation}] from the one [{author_institution}] in the XLS file. from the one searched in the XLS file, so will be skipped\n")
            continue
        else:
            print( text + f"\nThis author's SCOPUS record has the same affiliation [{affiliation}] as the one [{author_institution}] in the XLS file.\nThis author will be processed\n")
            with open(log_file_path, "a", encoding="utf-8") as file:
                file.write( text + f"\nThis author's SCOPUS record has the same affiliation [{affiliation}] as the one [{author_institution}] in the XLS file.\nThis author will be processed\n")

        author_articles = functions.get_author_articles( author_id , API_KEY )            # Gets the list of author articles
        
        print( f"This author has {len(author_articles)} articles with the XLS institution {author_institution} / Scopus institution {affiliation}\n")
        with open(log_file_path, "a", encoding="utf-8") as file:
            file.write( f"This author has {len(author_articles)} articles with the XLS institution {author_institution} / Scopus institution {affiliation}\n")
            
        articles_data = []        
        for k, author_article in enumerate( author_articles ):       

            author_article_elements = list( author_article.values() )  
            
            author_article_title    = author_article_elements[0]
            author_article_num_aut  = author_article_elements[1]
            print(f"\n\n##############\nXLS Author: {author_name} {author_surname} - Institution: {author_institution}\n")
            print(f"Article n. {k+1}/{len(author_articles)} - Title: {author_article_title}\n" )
            with open(log_file_path, "a", encoding="utf-8") as file:
                file.write(f"\n\n##############\nXLS Author: {author_name} {author_surname} - Institution: {author_institution}\n")
                file.write(f"Article n. {k+1}/{len(author_articles)} - Title: {author_article_title}\n" )
                    
            author_article_num_cit  = author_article_elements[2]
            author_article_doi      = author_article_elements[3]
            author_article_eid      = author_article_elements[4]  

            # Searches the article in the CSV file, to verify 
            # - if it is already found
            #       - for this author -> skip the article 
            #       - for another author -> write it for this author
            # - if it is not found in the CSV file -> write it for this author
            # This is done to avoid 
            # - reduce the queries with Scopus API
            # - writing the same article for the same author multiple times in the CSV file
           
            found_article_and_author_flag, article_data = functions.written_article_in_CSV( articles, author_article_eid, author_name, author_surname, author_institution ) 
            
            if found_article_and_author_flag :
                print( f"EID article code: {author_article_eid} , Author name {author_name} , Author surname {author_surname} , Author institution {author_institution}\n")
                print("This article has already been processed and written in the CSV file for this author, so it will be skipped\n")
                with open(log_file_path, "a", encoding="utf-8") as file:
                    file.write(f"EID article code: {author_article_eid} , Author name {author_name} , Author surname {author_surname} , Author institution {author_institution}\n")
                    file.write("This article has already been processed and written in the CSV file for this author, so it will be skipped\n")
                continue
            else:
                text = f"EID article code: {author_article_eid} , Author name {author_name} , Author surname {author_surname} , Author institution {author_institution} , Author AU_ID {author_id}\n"
                print( text )
        
                if article_data is not None :
                    print("This article has already been processed and written in the CSV file for another author: these data will be written for this author\n")
                    with open(log_file_path, "a", encoding="utf-8") as file:
                        file.write( text )
                        file.write( f"\nThis article has already been processed and written in the CSV file for another author: these data will be written for this author\n")
                    ( author_article_year, author_article_num_aut, author_article_num_references, author_article_num_ref , author_article_citing_years ) = article_data                   
                else:
                    print("This article has never been processed and written in the CSV file: the query will be done and these data will be written for this author\n")
                    with open(log_file_path, "a", encoding="utf-8") as file:
                        file.write( text )
                        file.write( f"\nThis article has never been processed and written in the CSV file: the query will be done and these data will be written for this author\n")
                                    
                    time.sleep(7) # Rallenta il processo di 7 secondi per evitare di superare il limite di richieste API

                    author_article_year = functions.get_article_year_by_eid( author_article_eid, API_KEY )
                    
                    author_article_authors = functions.get_authors_by_eid( author_article_eid, API_KEY )
                    author_article_num_aut = len( author_article_authors )      
                                       
                    article_references = functions.get_references_by_doi( author_article_doi ) # Gets the list of reference articles
                    author_article_num_references = len( article_references )          

                    # Gets the dois codes for the citing articles of the selected article
                    # then manages the citing articles to get the number of references in the citing articles and the years of the citing articles 
                    author_article_citing_dois = functions.get_citing_articles( author_article_eid , API_KEY )
                    author_article_num_ref , author_article_citing_years = functions.manage_citing_articles( author_article_citing_dois, API_KEY)

            current_article_data = {"name":         author_name ,
                                    "surname":      author_surname, 
                                    "institution":  functions.clean_field( author_institution ),
                                    "author_id":    author_id,
                                    "article_eid":  author_article_eid,
                                    "year":         author_article_year,
                                    "num_aut":      author_article_num_aut, 
                                    "num_cit":      author_article_num_cit, 
                                    "article_refs": author_article_num_references,
                                    "num_ref_in_citing": author_article_num_ref  ,
                                    "citing_years": functions.clean_field ( author_article_citing_years ) }

                       
            with open(csv_file_path, "a", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, delimiter="|", fieldnames=["name", "surname", "institution", "author_id", "article_eid", "year", "num_aut", "num_cit", "article_refs", "num_ref_in_citing", "citing_years"])       
                writer.writerows( [current_article_data] )
            
            articles_data.append( current_article_data )
            articles.append( current_article_data )
            
            with open(log_file_path, "a", encoding="utf-8") as file:
                file.write( f"Number of citations: {author_article_num_cit}\n")
                file.write( f"Number of references: {author_article_num_references}\n")
                file.write( f"Citing years: {author_article_citing_years}\n")
               
        
        num_articles = len( articles_data )
        print(f"\n\n############\nAuthor:\nName: { author_name }\nSurname: { author_surname}\nInstitution: { author_institution}\nSaved {num_articles} articles\n")
        for k in range (num_articles):
            print( f"Art. {k+1}/ {num_articles} ) {articles_data[k]}\n")
        with open(log_file_path, "a", encoding="utf-8") as file:
            file.write(f"\n\n############\nAuthor:\nName: { author_name }\nSurname: { author_surname}\nInstitution: { author_institution}\nSaved {num_articles} articles\n")
            for k in range (num_articles):
                file.write( f"Art. {k+1}/ {num_articles} ) {articles_data[k]}\n")
                

print(f"\n\nEnd of the search for author's articles in Scopus\n")





