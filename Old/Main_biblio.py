
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 19:21:41 2024

@author: Paolo Castellini
"""

import functions as functions
import pandas as pd

# Chiave API
API_KEY = "c81e40b973484fb83db5c697eadc3bea"



# Path to the Excel file
file_path = "misure.xlsx"

# Read the Excel file
df = pd.read_excel(file_path)

# Display the first few rows
#print(df.head())

colonna = df['Cognome e Nome']
ateneo =df["Ateneo"]

dati = []  
for ii, c in enumerate(colonna):     
    parti= c.split()
    cognome= parti[0]
    nome= parti[1]
    institution=ateneo[ii]
    


# Call the function
    result = functions.search_author_with_institution(API_KEY, nome, cognome, institution)
# Display the result
    for entry in result.get("search-results", {}).get("entry", []):
        print(f"Author Name: {entry.get('preferred-name', {}).get('surname')}, {entry.get('preferred-name', {}).get('given-name')}")
        #print(f"Institution: {entry.get('affiliation-current', {}).get('affiliation-name')}")
        #print(f"Scopus Author ID: {entry.get('dc:identifier')}")

    aut=str({entry.get('dc:identifier')})
    m=len(aut)
    AUTHOR_ID = aut[12:m-2]


# Scopus Author ID
#AUTHOR_ID = "55785672000"

# Recupera gli articoli pubblicati dall'autore
    articles = functions.get_author_articles(API_KEY, AUTHOR_ID)



    for jj, title in enumerate(articles):
        print(jj)

        values = list(title.values())

        num_aut=values[1]
        num_cit=values[2]
        article_doi=values[3]
        article_eid=values[4]

        year = functions.get_publication_year_using_crossref(article_doi)

        citing_dois = functions.OLD_get_citing_articles(API_KEY, article_eid)

        num_ref=[]
        for kk, c_doi in enumerate(citing_dois):

            references = functions.get_references_by_doi(c_doi)
            num_ref.append(len(references))  # Aggiunge i valori calcolati


#c_ref=references[1]

#ref_year=c_ref['year']


#year = fun.get_publication_year(article_doi)









  
    
    
        dati.append({"nome": nome ,"cognome": cognome, "Institution": institution,"AUTHOR_ID": AUTHOR_ID,"year":year,"num_aut": num_aut, "num_cit": num_cit, " num_ref_in_citing":  num_ref})

    
    








