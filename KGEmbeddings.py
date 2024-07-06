import numpy as np
from SPARQLWrapper import SPARQLWrapper, JSON
from gensim.models import Word2Vec
import networkx as nx
from collections import deque
import random

# Set up SPARQL endpoint
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def get_dbpedia_relations(entity):
    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT DISTINCT ?relation ?object
    WHERE {{
      <http://dbpedia.org/resource/{entity.replace(' ', '_')}> ?relation ?object .
      FILTER(STRSTARTS(STR(?relation), STR(dbo:)))
    }}
    LIMIT 1000
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [(result['relation']['value'], result['object']['value']) for result in results['results']['bindings']]

def get_wikipedia_title(dbpedia_uri):
    return dbpedia_uri.split('/')[-1].replace('_', ' ')

def random_walk(start_entity, walk_length=10):
    walk = [start_entity]
    for _ in range(walk_length - 1):
        relations = get_dbpedia_relations(walk[-1])
        entity_relations = [r for r in relations if r[1].startswith('http://dbpedia.org/resource/')]
        if not entity_relations:
            break
        _, next_entity = random.choice(entity_relations)
        walk.append(get_wikipedia_title(next_entity))
    return walk

def generate_walks(entities, num_walks=10, walk_length=10):
    all_walks = []
    for entity in entities:
        for _ in range(num_walks):
            all_walks.append(random_walk(entity, walk_length))
    return all_walks

def train_embeddings(walks):
    model = Word2Vec(sentences=walks, window=5, min_count=0, workers=4)
    return model

def find_path(start, end, model):
    graph = nx.Graph()
    queue = deque([(start, [])])
    visited = set()

    while queue:
        (vertex, path) = queue.popleft()
        if vertex not in visited:
            visited.add(vertex)

            if vertex == end:
                return path + [end]

            relations = get_dbpedia_relations(vertex)
            entity_relations = [r for r in relations if r[1].startswith('http://dbpedia.org/resource/')]

            for relation, next_entity in entity_relations:
                next_title = get_wikipedia_title(next_entity)
                if next_title not in visited:
                    if next_title in model.wv:
                        similarity = model.wv.similarity(end, next_title)
                        graph.add_edge(vertex, next_title, weight=-similarity)
                    else:
                        graph.add_edge(vertex, next_title, weight=0)
                    queue.append((next_title, path + [vertex]))

    # If no direct path is found, use shortest path in the graph
    if start in graph and end in graph:
        return None
    return None



start_entity = "Alexander the Great"
end_entity = "Anubis"

print("Generating random walks...")
walks = generate_walks([start_entity, end_entity], num_walks=50, walk_length=10)

print("Training embeddings...")
model = train_embeddings(walks)

print("Finding path...")
path = find_path(start_entity, end_entity, model)

if path:
    print("Path found:")
    for i in range(len(path) - 1):
        relations = get_dbpedia_relations(path[i])
        relation = next((rel for rel, obj in relations if get_wikipedia_title(obj) == path[i+1]), "Unknown")
        print(f"{path[i]} --[{relation.split('/')[-1]}]--> {path[i+1]}")
else:
    print("No path found")