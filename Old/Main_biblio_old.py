import functions as functions


# Chiave API
API_KEY = "c81e40b973484fb83db5c697eadc3bea"



first_name = "Paolo"
last_name = "Castellini"
institution = "Università Politecnica delle Marche"

# Call the function
result = functions.search_author_with_institution(API_KEY, first_name, last_name, institution)

# Display the result
for entry in result.get("search-results", {}).get("entry", []):
    print(f"Author Name: {entry.get('preferred-name', {}).get('surname')}, {entry.get('preferred-name', {}).get('given-name')}")
    print(f"Institution: {entry.get('affiliation-current', {}).get('affiliation-name')}")
    print(f"Scopus Author ID: {entry.get('dc:identifier')}")

aut=str({entry.get('dc:identifier')})
m=len(aut)
AUTHOR_ID = aut[12:m-2]


# Scopus Author ID
#AUTHOR_ID = "55785672000"

# Recupera gli articoli pubblicati dall'autore
articles = functions.get_author_articles(API_KEY, AUTHOR_ID)

title=articles[205]

values = list(title.values())


num_aut=values[1]
num_cit=values[2]
article_doi=values[3]
article_eid=values[4]


citing_dois = functions.OLD_get_citing_articles(API_KEY, article_eid)

c_doi=citing_dois[1];


references = functions.get_references_by_doi(c_doi)

c_ref=references[1]

ref_year=c_ref['year']


year = functions.get_publication_year_using_crossref(article_doi)

