from SPARQLWrapper import SPARQLWrapper, JSON
from sentence_transformers import SentenceTransformer, util

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Setup SPARQL endpoint
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"


def get_wikidata_id(label):
    """Get Wikidata Q-ID for a natural language label."""
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setReturnFormat(JSON)
    query = f'''
    SELECT ?item WHERE {{
      ?item rdfs:label "{label}"@en .
    }}
    LIMIT 1
    '''
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["item"]["value"]
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_property_label_from_web(uri):
    """Fetch human-readable label for a given property URI from the web."""
    import re
    import requests
    from bs4 import BeautifulSoup
    match = re.search(r'/P(\d+)$', uri) or re.search(r'P(\d+)', uri)
    prop_id = f'P{match.group(1)}' if match else None
    if not prop_id:
        return None
    url = f"https://www.wikidata.org/wiki/Property:{prop_id}"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        span = soup.find('span', class_='wikibase-title-label')
        if span:
            return span.text.strip()
    except Exception as e:
        print(f"Web scraping failed for {url}: {e}")
    return prop_id


def get_predicates_between(subject_id, object_id):
    """Get all predicates (uri, label) between two Q-IDs, always returning a label (never a URI as label)."""
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setReturnFormat(JSON)
    query = f'''
    SELECT ?predicate ?predicateLabel WHERE {{
      <{subject_id}> ?predicate <{object_id}> .
      OPTIONAL {{ ?predicate rdfs:label ?predicateLabel FILTER (lang(?predicateLabel) = 'en') }}
    }}
    '''
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]
        preds = []
        for r in bindings:
            uri = r.get("predicate", {}).get("value")
            label = r.get("predicateLabel", {}).get("value")
            # If label is missing or looks like a URI, fetch from web
            if (not label or label.startswith("http://") or label.startswith("https://")) and uri:
                label = get_property_label_from_web(uri)
            if uri and label:
                preds.append((uri, label))
        return preds
    except Exception as e:
        print(f"Query error: {e}")
        return []


def get_similarity(llm_predicate, kg_predicate_label):
    """Compute cosine similarity between LLM predicate and KG predicate label."""
    emb1 = model.encode(llm_predicate, convert_to_tensor=True)
    emb2 = model.encode(kg_predicate_label, convert_to_tensor=True)
    return util.cos_sim(emb1, emb2).item()


def validate_triple(subject, predicate, obj):
    """Validate an LLM triple using Wikidata."""
    subject_id = get_wikidata_id(subject)
    object_id = get_wikidata_id(obj)

    if not subject_id or not object_id:
        return {"status": "invalid", "reason": "Could not find entity IDs"}

    predicates = get_predicates_between(subject_id, object_id)
    if not predicates:
        return {"status": "unverified", "confidence": 0.0}

    # Check semantic similarity
    best_match = (None, 0)
    for pred_uri, pred_label in predicates:
        sim = get_similarity(predicate, pred_label)
        if sim > best_match[1]:
            best_match = (pred_label, sim)

    return {
        "status": "verified" if best_match[1] >= 0.75 else "weak_match",
        "subject": subject,
        "predicate_llm": predicate,
        "predicate_kg": best_match[0],
        "object": obj,
        "confidence": round(best_match[1], 2)
    }


# Example usage
triples_to_validate = [
    {"subject": "Nikola Tesla", "predicate": "studied at", "obj": "Graz University of Technology"},
    {"subject": "Albert Einstein", "predicate": "educated at", "obj": "ETH Zurich"}
]

for triple in triples_to_validate:
    result = validate_triple(**triple)
    print(result)