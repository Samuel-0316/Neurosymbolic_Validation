import spacy
from allennlp.predictors.predictor import Predictor
import allennlp_models.coref
import json

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Load AllenNLP coreference resolution model
coref_predictor = Predictor.from_path(
    "https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz"
)

def sentence_segmentation(text):
    doc = nlp(text)
    return [sent.text for sent in doc.sents]

def named_entity_recognition(sentence):
    doc = nlp(sentence)
    return {ent.text: ent.label_ for ent in doc.ents}

def resolve_coreferences(text):
    result = coref_predictor.predict(document=text)
    resolved = result['document']
    clusters = result['clusters']
    # Map index to word
    idx2word = {i: w for i, w in enumerate(resolved)}
    # Replace pronouns with their referents
    for cluster in clusters:
        main = " ".join([idx2word[i] for i in range(cluster[0][0], cluster[0][1]+1)])
        for mention in cluster[1:]:
            for i in range(mention[0], mention[1]+1):
                idx2word[i] = main
    return " ".join([idx2word[i] for i in range(len(idx2word))])

def extract_triples(sentence):
    doc = nlp(sentence)
    triples = []
    for token in doc:
        # Find subject-verb-object relations
        if token.dep_ == "ROOT":
            subj = [w for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
            obj = [w for w in token.rights if w.dep_ in ("dobj", "attr", "prep", "pobj")]
            if subj and obj:
                triples.append({
                    "subject": subj[0].text,
                    "predicate": token.lemma_,
                    "object": obj[0].text
                })
    return triples

def normalize_triple(triple):
    # Stub: Replace with Wikidata/DBpedia lookup as needed
    triple['subject'] = triple['subject'].title()
    triple['predicate'] = triple['predicate'].lower()
    triple['object'] = triple['object'].title()
    return triple

def classify_triple_type(triple):
    # Stub: Replace with ML classifier or heuristics
    return "factual"

def process_llm_output(text):
    # 1. Coreference resolution
    resolved_text = resolve_coreferences(text)
    # 2. Sentence segmentation
    sentences = sentence_segmentation(resolved_text)
    triples = []
    for sent in sentences:
        # 3. NER
        entities = named_entity_recognition(sent)
        # 4. Triple extraction
        extracted = extract_triples(sent)
        for triple in extracted:
            # 5. Normalize
            triple = normalize_triple(triple)
            # 6. Classify
            triple['type'] = classify_triple_type(triple)
            triples.append(triple)
    return triples

if __name__ == "__main__":
    llm_response = "Einstein developed relativity. He was born in Germany."
    triples = process_llm_output(llm_response)
    print(json.dumps(triples, indent=2))