# ner_extraction.py
import spacy
import pandas as pd

# Load spaCy model (English)
nlp = spacy.load("en_core_web_sm")  # or en_core_web_trf for transformer-based NER

def extract_entities(text):
    """
    Extract named entities from a given text.
    Returns a list of (entity_text, entity_label) tuples.
    """
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def process_corpus(df, text_column='Sentence'):
    """
    Process entire DataFrame to extract entities.
    Adds a new column 'entities' with list of tuples.
    """
    df['entities'] = df[text_column].apply(extract_entities)
    return df

if __name__ == "__main__":
    # Example usage
    df = pd.read_csv(r"D:\Sentiment_financial\data.csv")  
    df = process_corpus(df)
    df.to_csv("corpus_with_entities.csv", index=False)
    print("NER extraction completed! Saved to corpus_with_entities.csv")
