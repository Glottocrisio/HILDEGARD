import spacy

def enttype(text):
    # Load the English language model
    nlp = spacy.load("en_core_web_sm")

    # Process the text with spaCy
    doc = nlp(text)

    # Extract entities and their types
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print = ""
    for entity, entity_type in entities:
        print = f"Entity: {entity}, Type: {entity_type}"
    print(print)
    return print