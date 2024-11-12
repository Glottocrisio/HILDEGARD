from rdflib import Graph
import networkx as nx
import json
from sklearn.metrics import precision_score, recall_score, f1_score
import wikifier as w
from collections import Counter
import csv
import time
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import deque

def get_dbpedia_relations(entity):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
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

def shortest_path(start, end):
    queue = deque([(start, [])])
    visited = set()

    while queue:
        (vertex, path) = queue.popleft()
        if vertex not in visited:
            visited.add(vertex)

            if vertex == end:
                return path

            dbpedia_relations = get_dbpedia_relations(vertex)
            entity_relations = [r for r in dbpedia_relations if r[1].startswith('http://dbpedia.org/resource/')]

            for relation, next_entity in entity_relations:
                next_title = get_wikipedia_title(next_entity)
                if next_title not in visited:
                    queue.append((next_title, path + [(vertex, relation.split('/')[-1], next_title)]))

    return None  # Path not found


def run_with_metrics(start_entity, end_entity):
    print(f"Finding shortest path from '{start_entity}' to '{end_entity}'...")
    
    start_time = time.time()
    path, entities_explored = shortest_path(start_entity, end_entity)
    end_time = time.time()

    execution_time = end_time - start_time

    print("\nPerformance Metrics:")
    print(f"Execution Time: {execution_time:.2f} seconds")
    print(f"Entities Explored: {entities_explored}")

    if path:
        print(f"Path Length: {len(path)}")
        print("\nShortest path:")
        for step in path:
            print(f"{step[0]} --[{step[1]}]--> {step[2]}")
    else:
        print("No path found")

    return {
        "execution_time": execution_time,
        "entities_explored": entities_explored,
        "path_length": len(path) if path else None,
        "path_found": path is not None
    }


# Example usage
start_entity = "Anubis"
end_entity = "Alexander the Great"

#metrics = run_with_metrics(start_entity, end_entity)




import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def measure_execution_time(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    return end_time - start_time, result

def estimate_complexity(func, input_generator, min_n=10, max_n=1000, step=10):
    sizes = []
    times = []

    for n in range(min_n, max_n + 1, step):
        input_data = input_generator(n)
        execution_time = measure_execution_time(func, input_data)
        sizes.append(n)
        times.append(execution_time)

    return np.array(sizes), np.array(times)

def complexity_functions():
    return {
        'O(1)': (lambda n, a: a * np.ones_like(n), 'Constant'),
        'O(log n)': (lambda n, a: a * np.log(n), 'Logarithmic'),
        'O(n)': (lambda n, a: a * n, 'Linear'),
        'O(n log n)': (lambda n, a: a * n * np.log(n), 'Linearithmic'),
        'O(n^2)': (lambda n, a: a * n**2, 'Quadratic'),
        'O(n^3)': (lambda n, a: a * n**3, 'Cubic'),
        'O(2^n)': (lambda n, a: a * 2**n, 'Exponential')
    }

def fit_complexity(sizes, times):
    complexities = complexity_functions()
    best_complexity = None
    best_rmse = float('inf')

    for complexity, (func, name) in complexities.items():
        try:
            popt, _ = curve_fit(func, sizes, times)
            rmse = np.sqrt(np.mean((func(sizes, *popt) - times)**2))
            if rmse < best_rmse:
                best_rmse = rmse
                best_complexity = (complexity, name, func, popt)
        except:
            continue

    return best_complexity

def plot_complexity(sizes, times, complexity):
    plt.figure(figsize=(10, 6))
    plt.scatter(sizes, times, label='Measured times')
    plt.plot(sizes, complexity[2](sizes, *complexity[3]), 'r-', label=f'Fitted {complexity[0]}')
    plt.xlabel('Input size')
    plt.ylabel('Execution time (seconds)')
    plt.title(f'Time Complexity Analysis: {complexity[1]}')
    plt.legend()
    plt.show()



def dbpedia_spotlight(text, confidence=0.6,  language='it'):
    
    url = "https://api.dbpedia-spotlight.org/it/annotate"
    
    params = {
        "text": text,
        "confidence": confidence
    }
    
    # Headers for the API call
    headers = {
        "Accept": "application/json"
    }
    
    try:
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status() 
        
    
        result = response.json()
    
        annotations = []
        if "Resources" in result:
            for resource in result["Resources"]:
                annotation = {
                    "uri": resource["@URI"],
                    "surface_form": resource["@surfaceForm"],
                    #"offset": int(resource["@offset"]),
                    "types": resource["@types"].split(",") if "@types" in resource else []
                }
                annotations.append(annotation)
        
        return annotations
    
    except requests.exceptions.RequestException as e:
        print(f"Error calling DBpedia Spotlight API: {e}")
        return []


from tqdm import tqdm


def process_texts(input_file, output_file):

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = []
    
    # Process each text
    for item in tqdm(data, desc="Processing texts"):
        text = item['text']
        
        wikifier_results = w.CallWikifier(text)
        dbpedia_results = dbpedia_spotlight(text)
        
        result = {
            'text': text,
            'wikifier_annotations': wikifier_results,
            'dbpedia_annotations': dbpedia_results
        }
        
        results.append(result)
    
    # Write the results to the output JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Processing complete. Results saved to {output_file}")

# if __name__ == "__main__":
#     import argparse
    
#     parser = argparse.ArgumentParser(description="Process texts using Wikifier and DBpedia Spotlight APIs.")
#     parser.add_argument("input_file", help="Path to the input JSON file containing texts")
#     parser.add_argument("output_file", help="Path to the output JSON file for results")
    
#     args = parser.parse_args()
    
#process_texts("test_data_entity_linking_short.json", "wikifier_dbpediaspot_annotations.json")
    

def compare_annotations(input_file, output_file):
    # Read the input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = []
    overall_comparison = {
        'total_wikifier': 0,
        'total_dbpedia': 0,
        'total_common': 0,
        'total_only_wikifier': 0,
        'total_only_dbpedia': 0,
        'overall_wikifier_types': Counter(),
        'overall_dbpedia_types': Counter()
    }
    
    # Process each item in the input data
    for item in data:
        wikifier_annotations = item['wikifier_annotations']
        dbpedia_annotations = item['dbpedia_annotations']
        
        wikifier_count = len(wikifier_annotations)
        dbpedia_count = len(dbpedia_annotations)
        
        wikifier_uris = set(ann['surface_form'] for ann in wikifier_annotations)
        dbpedia_uris = set(ann['surface_form'] for ann in dbpedia_annotations)
        
        common_uris = wikifier_uris & dbpedia_uris
        only_wikifier = wikifier_uris - dbpedia_uris
        only_dbpedia = dbpedia_uris - wikifier_uris
        
        wikifier_types = Counter(type for ann in wikifier_annotations for type in ann['types'])
        dbpedia_types = Counter(type for ann in dbpedia_annotations for type in ann['types'])
        
        comparison = {
            'wikifier_count': wikifier_count,
            'dbpedia_count': dbpedia_count,
            'common_annotations': len(common_uris),
            'only_wikifier': len(only_wikifier),
            'only_dbpedia': len(only_dbpedia),
            'wikifier_types': dict(wikifier_types),
            'dbpedia_types': dict(dbpedia_types)
        }
        
        # Add comparison to the item
        item['comparison'] = comparison
        results.append(item)
        
        # Update overall comparison
        overall_comparison['total_wikifier'] += wikifier_count
        overall_comparison['total_dbpedia'] += dbpedia_count
        overall_comparison['total_common'] += len(common_uris)
        overall_comparison['total_only_wikifier'] += len(only_wikifier)
        overall_comparison['total_only_dbpedia'] += len(only_dbpedia)
        overall_comparison['overall_wikifier_types'].update(wikifier_types)
        overall_comparison['overall_dbpedia_types'].update(dbpedia_types)
    
    # Calculate averages
    num_texts = len(data)
    overall_comparison['avg_wikifier_per_text'] = overall_comparison['total_wikifier'] / num_texts
    overall_comparison['avg_dbpedia_per_text'] = overall_comparison['total_dbpedia'] / num_texts
    overall_comparison['avg_common_per_text'] = overall_comparison['total_common'] / num_texts
    
    # Convert Counters to regular dictionaries for JSON serialization
    overall_comparison['overall_wikifier_types'] = dict(overall_comparison['overall_wikifier_types'])
    overall_comparison['overall_dbpedia_types'] = dict(overall_comparison['overall_dbpedia_types'])
    
    # Add overall comparison to results
    results.append({'overall_comparison': overall_comparison})
    
    # Write the results to the output JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Comparison complete. Results saved to {output_file}")
    print("\nOverall Comparison:")
    print(json.dumps(overall_comparison, indent=2))

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Compare annotations from Wikifier and DBpedia Spotlight.")
#     parser.add_argument("input_file", help="Path to the input JSON file containing annotations")
#     parser.add_argument("output_file", help="Path to the output JSON file for comparison results")
    
#     args = parser.parse_args()
    
#compare_annotations("wikifier_dbpediaspot_annotations.json", "annotations_comparison_2.json")

# def extract_and_sum_comparisons(input_file, output_file):
#     # Initialize counters
#     total_wikifier_count = 0
#     total_dbpedia_count = 0
#     total_common_annotations = 0
#     total_only_wikifier = 0
#     total_only_dbpedia = 0

#     # Read the input JSON file
#     with open(input_file, 'r', encoding='utf-8') as f:
#         data = json.load(f)

#     # Process each item in the input data
#     for item in data:
#         if 'comparison' in item:
#             comparison = item['comparison']
#             total_wikifier_count += comparison.get('wikifier_count', 0)
#             total_dbpedia_count += comparison.get('dbpedia_count', 0)
#             total_common_annotations += comparison.get('common_annotations', 0)
#             total_only_wikifier += comparison.get('only_wikifier', 0)
#             total_only_dbpedia += comparison.get('only_dbpedia', 0)

#     # Prepare the data for CSV
#     csv_data = [
#         ['wikifier_count', total_wikifier_count],
#         ['dbpedia_count', total_wikifier_count],
#         ['common_annotations', total_common_annotations],
#         ['only_wikifier', total_only_wikifier],
#         ['only_dbpedia', total_only_dbpedia]
#     ]

#     # Write the results to the output CSV file
#     with open(output_file, 'w', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         writer.writerows(csv_data)

#     print(f"Extraction and summation complete. Results saved to {output_file}")
#     print("\nSummary:")
#     for row in csv_data:
#         print(f"{row[0]}: {row[1]}")

# # if __name__ == "__main__":
# #     parser = argparse.ArgumentParser(description="Extract and sum comparison data from JSON to CSV.")
# #     parser.add_argument("input_file", help="Path to the input JSON file containing comparisons")
# #     parser.add_argument("output_file", help="Path to the output CSV file for summed results")
    
# #     args = parser.parse_args()
    
# extract_and_sum_comparisons("annotations_comparison_2.json", "comparison_final_table.csv")

def average_node_degree(file_path):
    g = Graph()
    g.parse(file_path, format='ttl')

    node_degrees = {}

    for subject, predicate, obj in g:
        subject_str = str(subject)
        object_str = str(obj)

        if subject_str in node_degrees:
            node_degrees[subject_str] += 1
        else:
            node_degrees[subject_str] = 1

        if subject_str != object_str:
            if object_str in node_degrees:
                node_degrees[object_str] += 1
            else:
                node_degrees[object_str] = 1

    # Calculate the average degree
    total_degree = sum(node_degrees.values())
    average_degree = total_degree / len(node_degrees)

    # Print node degrees and average degree
    for node, degree in node_degrees.items():
        print(f"Node: {node}, Degree: {degree}")

    print(f"Average Degree: {average_degree}")
    return average_degree

def subgraph_centrality(file_path):
    g = Graph()
    g.parse(file_path, format='ttl')

    nx_graph = nx.Graph()

    for subject, predicate, obj in g:
        nx_graph.add_node(str(subject))
        nx_graph.add_node(str(obj))
        nx_graph.add_edge(str(subject), str(obj))
    subgraph_centralities = {}
    for node in nx_graph.nodes():
        subgraph_centrality = 0
        for subgraph in nx.generators.subgraph_centrality(nx_graph, node):
            subgraph_centrality += len(subgraph)
        subgraph_centralities[node] = subgraph_centrality
    return subgraph_centralities


def g_centrality(file_path, centrality_measure): 
    #The second parameter takes a character among 'b', 'c', 'p', 'e'. To be defined by a previous input.
    g = Graph()
    g.parse(file_path, format='ttl')

    # Create a NetworkX graph from the RDF graph
    nx_graph = nx.Graph()

    # Add nodes and edges to the NetworkX graph based on RDF triples
    for subject, predicate, obj in g:
        nx_graph.add_node(str(subject))
        nx_graph.add_node(str(obj))
        nx_graph.add_edge(str(subject), str(obj))
    
    if centrality_measure == 'b':
        centrality_measure = "Betweenness"
        centrality = nx.betweenness_centrality(nx_graph)
    elif centrality_measure == 'c':
        centrality_measure = "Closeness"
        centrality = nx.closeness_centrality(nx_graph)
    elif centrality_measure == 'p':
        centrality_measure = "PageRank"
        centrality = nx.pagerank(nx_graph)
    elif centrality_measure == 'e':
        centrality_measure = "Betweenness"
        centrality = nx.eigenvector_centrality(nx_graph)
    elif centrality_measure == 's':
        centrality_measure = "Subgraph"
        centrality = nx.subgraph_centrality(nx_graph)

    # Print node betweenness centrality values

    for node, centrality in centrality.items():
        print(f"Node: {node}, {centrality_measure}- Centrality: {centrality}")

    return centrality


#metr.average_node_degree("C:\\Users\\Palma\\Desktop\\PHD\\***\\battleIssusTriershortestpath.ttl")
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\***\\battleIssusTriershortestpath.ttl", 'b')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\***\\battleIssusTriershortestpath.ttl", 'c')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\***\\battleIssusTriershortestpath.ttl", 'p')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\***\\battleIssusTriershortestpath.ttl", 'e')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\***\\battleIssusTriershortestpath.ttl", 's')
