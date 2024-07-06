import requests
import random
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import deque


def get_wiki_links(title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "links",
        "pllimit": "max"
    }
    response = requests.get(url, params=params).json()
    page = next(iter(response["query"]["pages"].values()))
    return [link["title"] for link in page.get("links", [])]

def get_dbpedia_relation(entity1, entity2):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?relation
    WHERE {{
      <http://dbpedia.org/resource/{entity1.replace(' ', '_')}> ?relation <http://dbpedia.org/resource/{entity2.replace(' ', '_')}> .
      FILTER(STRSTARTS(STR(?relation), STR(dbo:)))
    }}
    LIMIT 1
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    if results["results"]["bindings"]:
        return results["results"]["bindings"][0]["relation"]["value"].split("/")[-1]
    return "unknown_relation"

def clickstream_walk(start, end, max_steps=20):
    current = start
    path = [current]
    relations = []
    
    for _ in range(max_steps):
        if current == end:
            return path, relations
        
        links = get_wiki_links(current)
        if end in links:
            path.append(end)
            relations.append(get_dbpedia_relation(current, end))
            return path, relations
        
        next_page = random.choice(links)
        path.append(next_page)
        relations.append(get_dbpedia_relation(current, next_page))
        current = next_page
    
    return path, relations

# Example usage
start_entity = "Alexander the Great"
end_entity = "Anubis"

path, relations = clickstream_walk(start_entity, end_entity)

print("Clickstream walk:")

print("First Method")
for i in range(len(path) - 1):
    print(f"{path[i]} --[{relations[i]}]--> {path[i+1]}")



def get_dbpedia_relationship(entity):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT DISTINCT ?relation ?object
    WHERE {{
      <http://dbpedia.org/resource/{entity.replace(' ', '_')}> ?relation ?object .
      FILTER(STRSTARTS(STR(?relation), STR(dbo:)))
    }}
    LIMIT 100
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [(result['relation']['value'], result['object']['value']) for result in results['results']['bindings']]

def get_wikipedia_title(dbpedia_uri):
    return dbpedia_uri.split('/')[-1].replace('_', ' ')


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def clickstream_walk_2(start, end, max_steps=20):
    current = start
    path = [current]
    relations = []
    
    for _ in range(max_steps):
        if current == end:
            return path, relations
        
        dbpedia_relations = get_dbpedia_relationship(current)
        
        # Filter relations that lead to other entities (not literal values)
        entity_relations = [r for r in dbpedia_relations if r[1].startswith('http://dbpedia.org/resource/')]
        
        if not entity_relations:
            return path + ["(No further relations found)"], relations
        
        # Sort relations by their similarity to the end entity
        sorted_relations = sorted(entity_relations, 
                                  key=lambda x: levenshtein_distance(get_wikipedia_title(x[1]), end))
        
        next_relation, next_entity = sorted_relations[0]
        next_title = get_wikipedia_title(next_entity)
        
        path.append(next_title)
        relations.append(next_relation.split('/')[-1])
        current = next_title
    
    return path + ["(Target not reached)"], relations


# Example usage
start_entity = "Anubis"
end_entity = "Alexander the Great"
print("Second Method")
path, relations = clickstream_walk_2(start_entity, end_entity)
for i in range(len(path) - 2):
    print(f"{path[i]} --[{relations[i]}]--> {path[i+1]}")

