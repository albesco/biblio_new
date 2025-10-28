
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 19:21:41 2024

@author: Paolo Castellini
"""

import functions as functions
import pandas as pd
import csv


# Chiave API Cast
API_KEY = "c81e40b973484fb83db5c697eadc3bea"

# Chiave API Caputo
#API_KEY="10f7de16ece6898e37b7f9c6d6a68eb7"

# Chiave API Scocco
#API_KEY="a4be5d6403465914a622246057f086e0"

# Path to the Excel file
file_path = "single.xlsx"

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
        
        num_cit=values[2]
        article_doi=values[3]
        article_eid=values[4]  
        
        #doi = "10.1016/j.heliyon.2024.e39875"  # Replace with the DOI of the paper you want
        authors = functions.get_authors_from_doi(article_doi)
        
        num_aut=len(authors)      
        
        ar_refs = functions.get_references_by_doi(article_doi)
        article_refs=len(ar_refs)          

        year = functions.get_publication_year_using_crossref(article_doi)
        
        citing_dois = functions.OLD_get_citing_articles(API_KEY, article_eid)
        
        citing_year=[]
        if len(citing_dois) > 0:
            num_ref=0
            for kk, c_doi in enumerate(citing_dois):
                references = functions.get_references_by_doi(c_doi)           
                num_ref=num_ref+1/len(references)
                y=functions.get_publication_year_using_crossref(c_doi)
                citing_year.append(y)
        else:
            num_ref=0
    
    
        dati.append({"nome": nome ,"cognome": cognome, "Institution": institution,"AUTHOR_ID": AUTHOR_ID,"article_eid":article_eid,"year":year,"num_aut": num_aut, "num_cit": num_cit, "article_refs": article_refs,"num_ref_in_citing":  num_ref,"citing_year": citing_year})

 
    


# Salva su file CSV
with open("Caputo.csv", "w", encoding="utf-8", newline="") as file:
    # Creare il writer
    writer = csv.DictWriter(file, fieldnames=["nome" ,"cognome", "Institution","AUTHOR_ID","article_eid","year","num_aut","num_cit","article_refs","num_ref_in_citing","citing_year"])
       
    
    # Scrivere l'intestazione
    writer.writeheader()
    
    # Scrivere i dati
    writer.writerows(dati)

print("Lista salvata su file")







