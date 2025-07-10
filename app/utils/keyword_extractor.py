import spacy
from collections import Counter

# This try-except block handles automatically downloading the model if it's missing.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_keywords(text, num_keywords=10):
    """
    Extracts the most common and relevant keywords from text.
    """
    if not text:
        return []
        
    doc = nlp(text.lower())
    keywords = []
    
    # Filter for nouns and proper nouns, excluding stop words and punctuation
    for token in doc:
        if (token.pos_ in ["PROPN", "NOUN"]) and not token.is_stop and not token.is_punct:
            keywords.append(token.lemma_)
            
    # Count the frequency of each keyword and return the most common ones
    most_common_keywords = [word for word, freq in Counter(keywords).most_common(num_keywords)]
    
    return most_common_keywords