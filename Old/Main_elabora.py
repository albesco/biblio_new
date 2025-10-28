# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 20:20:41 2024

@author: Paolo Castellini
"""

import pandas as pd
import matplotlib.pyplot as plt


# Read CSV file into a DataFrame
df = pd.read_csv('Caputo.csv')

# Display the first few rows
print(df.head())


# DATI
# data_all  lista completa
# data dati senza autori
# unique_data articoli non ripetuti
# unique_authors  autori non ripetuti


data = df.iloc[:, 4:].to_dict(orient='records')

#Elimina articoli ripetuti
seen = set()
unique_data = []
for row in data:
    if row['article_eid'] not in seen:
        seen.add(row['article_eid'])
        unique_data.append(row)
unique_data = pd.DataFrame(unique_data)


# Numero autori medio per anno
years = ()
for year in range(1980, 2025):  # range from 1980 to 2024
    years += (year,)

average_authors=[]
for year in range(1980, 2025):  # range from 1980 to 2024
    ud_year= unique_data[unique_data['year'] == year]
    average_authors.append(ud_year['num_aut'].mean())



# Create the plot
plt.figure(figsize=(8, 5))
plt.plot(years, average_authors, marker='o', linestyle='-', color='b', label='Average Authors')

# Add labels, title, and legend
plt.xlabel('Years')
plt.ylabel('Average Authors')
plt.title('Average Authors per Year')
plt.grid(True)
plt.legend()

# Show the plot
plt.show()


# Numero references medio per anno
average_refs=[]
for year in range(1980, 2025):  # range from 1980 to 2024
    ud_year= unique_data[unique_data['year'] == year]
    average_refs.append(ud_year['article_refs'].mean())

# Create the plot
plt.figure(figsize=(8, 5))
plt.plot(years, average_refs, marker='o', linestyle='-', color='b', label='Average Refs')

# Add labels, title, and legend
plt.xlabel('Years')
plt.ylabel('Average Refs')
plt.title('Average Refs per Year')
plt.grid(True)
plt.legend()

# Show the plot
plt.show()




#Estrazione lista autori
data_all = df.iloc[:,:].to_dict(orient='records')

seen = set()
unique_author = []
for row in data_all:
    if row['AUTHOR_ID'] not in seen:
        seen.add(row['AUTHOR_ID'])
        unique_author.append(row)



# Calcolo dell H-index e del C-index
h_authors=[]
cit_authors=[]
C_authors=[]
cit_authors_weight=[]
for author in unique_author:  
    unique_aut_id = author.pop("AUTHOR_ID")
    # H
    num_cit_vector= df[df["AUTHOR_ID"] == unique_aut_id]["num_cit"].tolist()
    num_cit_vector=sorted(num_cit_vector, reverse=True)
    h_index=0
    n_cit=0
    for ii,n in enumerate(num_cit_vector):
        n_cit=n_cit+n
        if n>=ii+1:
            h_index+=1
    h_authors.append(h_index)
    cit_authors.append(n_cit)
    # C
    num_cit_v_weight= df[df["AUTHOR_ID"] == unique_aut_id]["num_ref_in_citing"].tolist()
    num_cit_v_weight=sorted( num_cit_v_weight, reverse=True)
    C_index=0
    C_cit=0
    for ii,n in enumerate(num_cit_v_weight):
        C_cit=C_cit+n
        if 10*n>=ii+1:
            C_index+=1
    h_authors.append(C_index)
    cit_authors_weight.append(C_cit)

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Calcolo dell andamento di H-index nel tempo
h_authors=[]
for author in unique_author:  
    unique_aut_id = author.pop("AUTHOR_ID")
    # H
    citing_year= df[df["AUTHOR_ID"] == unique_aut_id]["citing_year"].tolist()
    citing_year=sorted(citing_year, reverse=True)
    
    
    
    
    
    
    
    h_index=0
    n_cit=0
    for ii,n in enumerate(num_cit_vector):
        n_cit=n_cit+n
        if n>=ii+1:
            h_index+=1
    h_authors.append(h_index)
    cit_authors.append(n_cit)
    # C
    num_cit_v_weight= df[df["AUTHOR_ID"] == unique_aut_id]["num_ref_in_citing"].tolist()
    num_cit_v_weight=sorted( num_cit_v_weight, reverse=True)
    C_index=0
    C_cit=0
    for ii,n in enumerate(num_cit_v_weight):
        C_cit=C_cit+n
        if 10*n>=ii+1:
            C_index+=1
    h_authors.append(C_index)
    cit_authors_weight.append(C_cit)

