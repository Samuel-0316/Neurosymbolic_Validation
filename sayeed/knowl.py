from SPARQLWrapper import SPARQLWrapper, JSON

# Subject: Douglas Adams (Q42), Predicate: Educated at (P69)
subject = "wd:Q42"
predicate = "wdt:P69"

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

sparql.setQuery(f"""
SELECT ?objectLabel WHERE {{
  {subject} {predicate} ?object .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
""")

results = sparql.query().convert()

print("Object(s) for given subject and predicate:")
print("------------------------------------------")
for r in results["results"]["bindings"]:
    print(r["objectLabel"]["value"])