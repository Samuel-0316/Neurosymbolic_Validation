from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from bs4 import BeautifulSoup

def get_wikidata_id(label, is_property=False):
    """Get Wikidata ID from a label."""
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)
    try:
        if is_property:
            query = f'''
            SELECT ?property WHERE {{
                ?property rdfs:label "{label}"@en;
                          a wikibase:Property .
            }}
            LIMIT 1'''
        else:
            query = f'''
            SELECT ?item WHERE {{
                ?item rdfs:label "{label}"@en .
            }}
            LIMIT 1'''
        sparql.setQuery(query)
        results = sparql.query().convert()
        if results["results"]["bindings"]:
            key = list(results["results"]["bindings"][0].keys())[0]
            return results["results"]["bindings"][0][key]["value"]
        return None
    except Exception as e:
        print(f"Error fetching Wikidata ID: {e}")
        return None

def get_property_label_from_web(property_uri):
    """Fetch the human-readable label from Wikidata property page."""
    import re
    match = re.search(r'/P(\d+)$', property_uri) or re.search(r'P(\d+)', property_uri)
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

def query_predicates(subject_label, object_label):
    """Print all predicates connecting subject and object labels, in both directions (only label, no URI)."""
    subject_id = get_wikidata_id(subject_label)
    object_id = get_wikidata_id(object_label)
    if not subject_id or not object_id:
        return
    for direction, s, o in [(f"{subject_label} → {object_label}", subject_id, object_id)]:
        print(f"Predicates connecting '{direction}':\n------------------------------------------")
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        sparql.setReturnFormat(JSON)
        query = f'''
        SELECT ?property ?propertyLabel WHERE {{
            <{s}> ?property <{o}> .
            OPTIONAL {{ ?property rdfs:label ?propertyLabel FILTER (lang(?propertyLabel) = 'en') }}
        }}'''
        try:
            sparql.setQuery(query)
            results = sparql.query().convert()
            bindings = results["results"]["bindings"]
            if bindings:
                for r in bindings:
                    label = r.get("propertyLabel", {}).get("value")
                    uri = r.get("property", {}).get("value")
                    if not label and uri:
                        label = get_property_label_from_web(uri)
                    if label:
                        print(label)
            else:
                print("No predicates found in this direction.")
        except Exception:
            pass

# Example usage
query_predicates("Nikola Tesla", "Graz University of Technology")

