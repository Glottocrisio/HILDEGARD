from rdflib import Graph
import networkx as nx

def average_node_degree(file_path):
    g = Graph()
    g.parse(file_path, format='ttl')

    node_degrees = {}

    # Calculate node degrees
    for subject, predicate, obj in g:
        # Convert subject and object to strings
        subject_str = str(subject)
        object_str = str(obj)

        # Update node degrees for subjects
        if subject_str in node_degrees:
            node_degrees[subject_str] += 1
        else:
            node_degrees[subject_str] = 1

        # Update node degrees for objects (if they are different from subjects)
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
    # Print node betweenness centrality values

    for node, centrality in centrality.items():
        print(f"Node: {node}, {centrality_measure}- Centrality: {centrality}")

    return centrality