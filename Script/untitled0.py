# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 09:28:07 2024

@author: Paolo Castellini
"""

import requests

def get_authors_from_doi(doi):
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

# Example usage
doi = "10.1016/j.heliyon.2024.e39875"  # Replace with the DOI of the paper you want
authors = get_authors_from_doi(doi)
print("Authors:")
for author in authors:
    print(author)
