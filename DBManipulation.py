from neo4j import GraphDatabase



def find_related(tx, keyword):
    query = ("MATCH (n) WHERE ANY(propValue IN [prop in keys(n) | n[prop]] WHERE propValue CONTAINS '" + str(keyword) + "') OPTIONAL MATCH (n)-[r]-(relatedNode) RETURN n, COLLECT(DISTINCT r) AS relationships, relatedNode")
    result = []
    for record in tx.run(query, keyword=keyword):
        result.append(record)
        print(record["n"])
        print(record["relationships"])
    return result

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

def create_link(tx, link, node_type1:str, node_type2:str):
    query = (f"MATCH (d) where d.ns0__variable=\"{node_type1}\" MATCH (t) where t.ns0__variable=\"{node_type2}\" MATCH (d)<-[:ns0__binding]-(commonNode)- [:ns0__binding]->(t) CREATE (d)-[:{link}]->(t);")
    for record in tx.run(query, link=link):
        print(record["n"])


def delete(tx, subgraph):
    query = ("MATCH (n) WHERE NOT n.ns0__value IN " + str(subgraph) + " RETURN n;")
    for record in tx.run(query, subgraph=subgraph):
        uri = record["n"]._properties["uri"]
        tx.run("MATCH (n) WHERE n.uri=$uri DETACH DELETE n", uri=uri)

def insert_triples(tx, triple):
    query = """
    MERGE (s:Subject {name: $subject})
    MERGE (o:Object {name: $object})
    MERGE (s)-[:RELATIONSHIP {property: $predicate}]->(o)
    """
    tx.run(query, subject=triple['subject'], predicate=triple['predicate'], object=triple['object'])

# Floyd Warshall Algorithm
#Initialize distances
#MATCH (o:Object)
#SET o.distance = CASE WHEN o = $startObject THEN 0 ELSE 9999 END

# Iterate to find shortest paths
#UNWIND range(1, size((o:Object))) AS _i
#MATCH (a:Object)-[ab:CONNECTED_TO]->(b:Object)
#WHERE a <> b
#WITH a, b, ab.weight AS weight
#MATCH (b)-[bc:CONNECTED_TO]->(c:Object)
#WHERE b <> c
#WITH a, b, c, weight + bc.weight AS newWeight
#WHERE a.distance + newWeight < c.distance
#SET c.distance = a.distance + newWeight
     

#Momentarily, KGs are at disposal only in Turtle Format

def importKnowledgebase(self, datapath):
    with open(datapath, 'r') as file:
        if datapath[0] != "h":
            datapath = "file:///" + datapath.replace("\\", "/")
        if datapath[-3:] == "csv":
            query = ("LOAD CSV WITH HEADERS FROM '" + str(datapath) +"' AS row CREATE (:Object {cultobj: row.cultobj, title: row.title,  museum: row.museo,  description: row.descr});")
        else: #we suppose that the available fromats are only csv and ttl. This option captures also the case of a uri ending in ".git"
            query = ("CALL n10s.rdf.import.fetch(\"" + str(datapath) +"\",\"Turtle\");") # {{handleVocabUris: 'IGNORE', handleMultival: 'ARRAY', commitSize: 500, nodeCacheSize: 200000}})
        for record in self.run(query, datapath=datapath):
            print(record)
