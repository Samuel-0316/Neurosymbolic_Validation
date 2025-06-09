import requests
import json
import time

# Wikidata SPARQL endpoint
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

def get_sparql_query(offset=0):
    return """
SELECT DISTINCT ?disease ?diseaseLabel ?property ?propertyLabel ?value ?valueLabel WHERE {
  {
    ?disease wdt:P31 wd:Q12136 .        # Instance of disease
  } UNION {
    ?disease wdt:P31/wdt:P279* wd:Q12136 .  # Instance of subclass of disease
  } UNION {
    ?disease wdt:P31 wd:Q2057971 .      # Instance of medical condition
  } UNION {
    ?disease wdt:P31 wd:Q9190427 .      # Instance of disorder
  }
  ?disease ?property ?value .            # Get all related triples
  FILTER(STRSTARTS(STR(?property), "http://www.wikidata.org/prop/direct/")) .

  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "en" .
  }
}
LIMIT 1000
OFFSET """ + str(offset)

def fetch_medical_diseases():
    headers = {
        "Accept": "application/json",
        "User-Agent": "Disease Data Collection Script/1.0"
    }
    
    all_results = []
    offset = 0
    total_processed = 0
    
    while True:
        query = get_sparql_query(offset)
        params = {
            "query": query
        }

        try:
            response = requests.get(SPARQL_ENDPOINT, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data['results']['bindings']
                
                if not results:  # No more results
                    break
                    
                for item in results:
                    disease = {
                        "disease_id": item['disease']['value'].split("/")[-1],
                        "disease_label": item['diseaseLabel']['value'],
                        "predicate_id": item['property']['value'].split("/")[-1],
                        "predicate_label": item['propertyLabel']['value'],
                        "object_id": item['value']['value'].split("/")[-1] if "wikidata.org" in item['value']['value'] else None,
                        "object_label": item['valueLabel']['value'] if 'valueLabel' in item else item['value']['value']
                    }
                    all_results.append(disease)
                
                total_processed += len(results)
                print(f"✅ Processed {total_processed} entries...")
                
                # Save intermediate results every 5000 entries
                if total_processed % 5000 == 0:
                    with open("medical_diseases.json", "w", encoding='utf-8') as f:
                        json.dump(all_results, f, indent=2, ensure_ascii=False)
                    print(f"💾 Saved intermediate results ({total_processed} entries)")
                
                offset += 1000  # Move to next batch
                time.sleep(1)  # Be nice to Wikidata servers
                
            else:
                print(f"❌ SPARQL query failed with status code {response.status_code}")
                print(response.text)
                break
                
        except Exception as e:
            print(f"❌ Error occurred: {str(e)}")
            break

    # Save final results
    with open("medical_diseases.json", "w", encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"✅ Complete! Total entries saved: {len(all_results)}")

if __name__ == "__main__":
    print("Starting to fetch disease data from Wikidata...")
    fetch_medical_diseases()