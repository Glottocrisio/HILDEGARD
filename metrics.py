from rdflib import Graph
import networkx as nx

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




#metr.average_node_degree("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\battleIssusTriershortestpath.ttl")
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\battleIssusTriershortestpath.ttl", 'b')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\battleIssusTriershortestpath.ttl", 'c')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\battleIssusTriershortestpath.ttl", 'p')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\battleIssusTriershortestpath.ttl", 'e')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\battleIssusTriershortestpath.ttl", 's')

#metr.average_node_degree("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\alexander2pompeishortpath.ttl")
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\alexander2pompeishortpath.ttl", 'b')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\alexander2pompeishortpath.ttl", 'c')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\alexander2pompeishortpath.ttl", 'p')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\alexander2pompeishortpath.ttl", 'e')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\alexander2pompeishortpath.ttl", 's')

#metr.average_node_degree("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\Entities_shortest_Path_Alessandro_Pompei.ttl")
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\Entities_shortest_Path_Alessandro_Pompei.ttl", 'b')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\Entities_shortest_Path_Alessandro_Pompei.ttl", 'c')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\Entities_shortest_Path_Alessandro_Pompei.ttl", 'p')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\Entities_shortest_Path_Alessandro_Pompei.ttl", 'e')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\Entities_shortest_Path_Alessandro_Pompei.ttl", 's')

#metr.average_node_degree("C:\\Users\Palma\\Desktop\\PHD\\HILD&GARD\\oggetticulturalimuseoarcheologiconazionaleitmerged.ttl")
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\oggetticulturalimuseoarcheologiconazionaleitmerged.ttl", 'b')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\oggetticulturalimuseoarcheologiconazionaleitmerged.ttl", 'c')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\oggetticulturalimuseoarcheologiconazionaleitmerged.ttl", 'p')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\oggetticulturalimuseoarcheologiconazionaleitmerged.ttl", 'e')
#metr.g_centrality("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\oggetticulturalimuseoarcheologiconazionaleitmerged.ttl", 's')
