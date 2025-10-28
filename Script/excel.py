# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 19:21:41 2024

@author: Paolo Castellini
"""

import pandas as pd

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
    
    
    
    
    
    dati.append({"nome": nome ,"cognome": cognome, "Institution": institution})

    
    
    
#istituzione = parti[2]