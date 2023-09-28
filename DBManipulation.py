from neo4j import GraphDatabase



def find_related(tx, name):
    query = ("MATCH (n) WHERE ANY(propValue IN [prop in keys(n) | n[prop]] WHERE propValue CONTAINS '" + str(name) + "') OPTIONAL MATCH (n)-[r]-(relatedNode) RETURN n, COLLECT(DISTINCT r) AS relationships, relatedNode")
    for record in tx.run(query, name=name):
        print(record["n"])
        print(record["relationships"])

def find_related_key(tx, value):
    query = ("MATCH (n) WHERE ANY(propValue IN [prop in keys(n) | n[prop]] WHERE propValue CONTAINS '" + str(value) + "') ""RETURN keys(n)")
    for record in tx.run(query, value=value):
        print(record["n"])

def find_related_descr(tx, element_id):
    query = ("MATCH (n) WHERE n.ns0__variable = \"title\" AND n.ns0__value = \"" + str(element_id) + "\" MATCH (n)<-[:ns0__binding]-(linkedNode)-[:ns0__binding]->(descr) WHERE descr.ns0__variable=\"descr\" RETURN DISTINCT descr.ns0__value as descr  LIMIT 1")
    for record in tx.run(query, element_id=element_id):
        print(record["descr"])

def all_pairs_shortest_path(tx, graphName):
    query = (   "CALL gds.alpha.allShortestPaths.stream(graphName: "+ str(graphName) +",configuration: map) YIELD sourceNodeId, targetNodeId, distance")
    for record in tx.run(query, name=name):
        print(record["n"])

def shortest_path(tx, nnodes):
    query = ("MATCH (start:StartNode {property_key: 'property_value'}), (end:EndNode {property_key: 'property_value'}) MATCH path = shortestPath((start)-[*]-(end)) RETURN path")
    for record in tx.run(query, names=names):
        print(record["n"])

def create_link(tx, link):
    query = ("MATCH (d) where d.ns0__variable=\"descr\" MATCH (t) where t.ns0__variable=\"title\" MATCH (d)<-[:ns0__binding]-(commonNode)- [:ns0__binding]->(t) CREATE (d)-[:"+str(link)+"]->(t);")
    for record in tx.run(query, link=link):
        print(record["n"])
     
