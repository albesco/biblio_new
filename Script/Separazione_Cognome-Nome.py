import re

def extract_surname_and_name(full_name):
    """
    Extracts surname and name from a full name string, considering specific formatting rules.

    Args:
        full_name (str): The full name string (e.g., "ROSSI mario antonio").

    Returns:
        tuple: A tuple containing the surname (str) and the formatted name (str), or (None, None) if the format is invalid.
    """
    words = full_name.split()
    if not words:
        return None, None

    surname_words = []
    name_words = []
    
    # Identify surname words (all uppercase)
    for word in words:
        if word.isupper():
            surname_words.append(word)
        else:
            break
    
    # Identify name words (all lowercase or title case)
    name_words = words[len(surname_words):]

    if not surname_words or not name_words:
        return None, None

    surname = " ".join(surname_words)

    # Format name words to title case
    formatted_name_words = [word.capitalize() for word in name_words]
    name = " ".join(formatted_name_words)

    return surname, name

# Example usage within the main.py file:
# ... inside the loop ...

# Old line:
# surname_name = col_SurnameName[k].split()

# New lines:

full_name = "MAGGI SILI Valentina Roberta"
surname, name = extract_surname_and_name( full_name )


