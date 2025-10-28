# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 10:30:14 2024

@author: Paolo Castellini
"""
import requests

def search_author_with_institution(api_key, first_name, last_name, institution):
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
        print(f"An error occurred: {e}")
        return None







# Replace 'YOUR_API_KEY' with your actual API key
API_KEY = "c81e40b973484fb83db5c697eadc3bea"

# Example search for author "John Doe" at "Harvard University"
first_name = "Paolo"
last_name = "Castellini"
institution = "Università Politecnica delle Marche"

# Call the function
result = search_author_with_institution(API_KEY, first_name, last_name, institution)

# Display the result
if result:
    print("Search Results:")
    for entry in result.get("search-results", {}).get("entry", []):
        print(f"Author Name: {entry.get('preferred-name', {}).get('surname')}, {entry.get('preferred-name', {}).get('given-name')}")
        print(f"Institution: {entry.get('affiliation-current', {}).get('affiliation-name')}")
        print(f"Scopus Author ID: {entry.get('dc:identifier')}")
        print()




