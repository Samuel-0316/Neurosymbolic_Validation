from SPARQLWrapper import SPARQLWrapper, JSON

def get_wikidata_id(label, is_property=False):
    """Helper function to get Wikidata ID from a label"""
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)
    
    try:
        if is_property:
            query = f"""
            SELECT ?property WHERE {{
                ?property rdfs:label "{label}"@en;
                          a wikibase:Property .
            }}
            LIMIT 1
            """
        else:
            query = f"""
            SELECT ?item WHERE {{
                ?item rdfs:label "{label}"@en .
            }}
            LIMIT 1
            """
        
        sparql.setQuery(query)
        results = sparql.query().convert()
        
        if results["results"]["bindings"]:
            key = list(results["results"]["bindings"][0].keys())[0]
            return results["results"]["bindings"][0][key]["value"]
        return None
    
    except Exception as e:
        print(f"Error fetching Wikidata ID: {e}")
        return None

def query_wikidata(subject_label, predicate_label):
    """Query Wikidata using natural language labels"""
    # Get Wikidata IDs for the labels
    subject_id = get_wikidata_id(subject_label)
    predicate_entity = get_wikidata_id(predicate_label, is_property=True)
    
    if not subject_id or not predicate_entity:
        print("Could not find Wikidata IDs for the given labels.")
        return
    
    # Convert property entity to direct property format
    direct_predicate = predicate_entity.replace("/entity/", "/prop/direct/")
    
    print(f"Found: Subject={subject_id}, Predicate={direct_predicate}")
    
    try:
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        sparql.setReturnFormat(JSON)
        
        query = f"""
        SELECT ?objectLabel WHERE {{
            <{subject_id}> <{direct_predicate}> ?object .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
        
        sparql.setQuery(query)
        results = sparql.query().convert()
        
        print(f"\nResults for '{subject_label}' and '{predicate_label}':")
        print("------------------------------------------")
        if results["results"]["bindings"]:
            for r in results["results"]["bindings"]:
                print(r["objectLabel"]["value"])
        else:
            print("No results found")
    
    except Exception as e:
        print(f"Query failed: {e}")

# Example usage
query_wikidata("Douglas Adams", "educated at")
query_wikidata("Albert Einstein", "educated at")
#query_wikidata("Marie Curie", "award received")
# Example usage
