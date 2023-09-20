from neo4j import GraphDatabase



def find_related(tx, name):
    query = ("MATCH (n) WHERE ANY(propValue IN [prop in keys(n) | n[prop]] WHERE propValue CONTAINS '" + str(name) + "') ""RETURN n")
    for record in tx.run(query, name=name):
        print(record["n"])

def find_related_key(tx, name):
    query = ("MATCH (n) WHERE ANY(propValue IN [prop in keys(n) | n[prop]] WHERE propValue CONTAINS '" + str(name) + "') ""RETURN keys(n)")
    for record in tx.run(query, name=name):
        print(record["n"])

def find_related_value(tx, name):
    query = ("MATCH (n) WHERE ANY(propValue IN [prop in keys(n) | n[prop]] WHERE propValue CONTAINS '" + str(name) + "') ""RETURN keys(n)")
    for record in tx.run(query, name=name):
        print(record["n"])

def all_pairs_shortest_path(tx, graphName):
    query = (   "CALL gds.alpha.allShortestPaths.stream(graphName: "+ str(graphName) +",configuration: map) YIELD sourceNodeId, targetNodeId, distance")
    for record in tx.run(query, name=name):
        print(record["n"])

def shortest_path(tx, nnodes):
    query = ("MATCH (start:StartNode {property_key: 'property_value'}), (end:EndNode {property_key: 'property_value'}) MATCH path = shortestPath((start)-[*]-(end)) RETURN path")
    for record in tx.run(query, names=names):
        print(record["n"])

     
