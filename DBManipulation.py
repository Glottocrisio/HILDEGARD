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

def find_related_descr_turtle(tx, element_id):
    query = ("MATCH (n) WHERE n.ns0__variable = \"title\" AND n.ns0__value = \"" + str(element_id) + "\" MATCH (n)<-[:ns0__binding]-(linkedNode)-[:ns0__binding]->(descr) WHERE descr.ns0__variable=\"descr\" RETURN DISTINCT descr.ns0__value as descr  LIMIT 1")
    for record in tx.run(query, element_id=element_id):
        print(record["descr"])

def find_related_descr_json(tx, element_id):
    query = ("MATCH (n) ,(descr)  WHERE n.value = \"" + str(element_id) + "\" AND (n)<-[:defines]-(descr) RETURN DISTINCT descr.value as descr LIMIT 1")
    for record in tx.run(query, element_id=element_id):
        print(record["descr"])

def all_pairs_shortest_path(tx, graphName):
    query = (   "CALL gds.alpha.allShortestPaths.stream(graphName: "+ str(graphName) +",configuration: map) YIELD sourceNodeId, targetNodeId, distance")
    for record in tx.run(query, name=graphName):
        print(record["n"])

def shortest_path(tx):
    query = ("MATCH (start:StartNode {property_key: 'property_value'}), (end:EndNode {property_key: 'property_value'}) MATCH path = shortestPath((start)-[*]-(end)) RETURN path")
    for record in tx.run(query):
        print(record["n"])

def create_link_turtle(tx, link, node_type1:str, node_type2:str):
    query = (f"MATCH (d) where d.ns0__variable=\"{node_type1}\" MATCH (t) where t.ns0__variable=\"{node_type2}\" MATCH (d)<-[:ns0__binding]-(commonNode)- [:ns0__binding]->(t) CREATE (d)-[:{link}]->(t);")
    for record in tx.run(query, link=link):
        print(record["n"])

def create_link_json(tx, node_type1:str, node_type2:str, link="P67:refers_to"):
    query = (f"MATCH (d) WHERE d.value=\"{node_type1}\" MATCH (t) WHERE t.name=\"{node_type2}\"  CREATE (d)-[{link}]->(t);")
    for record in tx.run(query, link=link):
        print(record["n"])

def delete(tx, subgraph):
    query = ("MATCH (n) WHERE NOT n.ns0__value IN " + str(subgraph) + " RETURN n;")
    for record in tx.run(query, subgraph=subgraph):
        uri = record["n"]._properties["uri"]
        tx.run("MATCH (n) WHERE n.uri=$uri DETACH DELETE n", uri=uri)

def insert_triples(tx, triple):
    labels = [key for key in triple.keys() if key != 'cidoc-relation']
    query = (
        "MERGE (s:" + str(labels[0]) + " {name: $subject}) "
        "MERGE (o:" + str(labels[1]) + " {name: $object}) "
        "MERGE (s)-[:" + triple['cidoc-relation'] + "]->(o)"
    )
    tx.run(query, subject=triple[labels[0]], object=triple[labels[1]])

def merge_homonym_nodes(tx, nodeName):
    
    query = (
        "MATCH (n:Node)"
        "WITH n.name AS " + str(nodeName) + ", collect(n) AS nodes"
        "WHERE size(nodes) > 1"
        "CALL apoc.refactor.mergeNodes(nodes) YIELD node"
        "RETURN node"
    )
    tx.run(query, nodeName=nodeName)
    
def link_similar_nodes(tx):
    query = (
        "MATCH (n:title), (m:title)"
        "WITH SPLIT(m.value,' ')[0] as token"
        "WHERE n.value <> m.value "
        "AND apoc.text.levenshteinSimilarity(n.value,token)  > 0.85 "
        "AND size(n.value)>4"
        "MERGE (n)-[P130:shows_features_of]->(m)"
    )
    tx.run(query)
    
def initialize_graph(tx):
    query = (
       
        "CALL n10s.graphconfig.init()"
        )
    tx.run(query)

def create_constraint(tx):
    query = (
       "CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource)"
        "REQUIRE r.uri IS UNIQUE;"
        )
    tx.run(query)

def assign_entity_types(tx):
    query = (
        "MATCH (museum)-[r]->() "
        "WHERE r.name = ':contains' "
        "SET museum.type = 'museum' "
        "MATCH (cultobj)-[r]->() "
        "WHERE r.name = ':is_about' "
        "SET cultobj.type = 'cultobj' "
        "MATCH (descr)-[r]->() "
        "WHERE r.name = ':defines' "
        "SET descr.type = 'descr'"
    )
    tx.run(query)

def assign_relationship_names(tx):
    query = (
        "MATCH ()-[r]->() "
        "SET r.name = type(r)"
    )
    tx.run(query)


def remove_descr_type(tx):
    query = (
        "MATCH (n) "
        "WHERE n.name CONTAINS 'http://dbpedia.org/' AND n.type = 'descr' "
        "REMOVE n.type"
    )
    tx.run(query)

def set_dbpedia_types(tx):
    query = (
        "MATCH ()-[r]->() "
        "WHERE r.name STARTS WITH 'http://dbpedia.org/ontology' "
        "SET r.type = 'dbpedia_relation' "
        "MATCH (e) "
        "WHERE e.name STARTS WITH 'http://dbpedia.org/resource' "
        "SET e.type = 'dbpedia_entity'"
    )
    tx.run(query)


def set_cidoc_crm_relationships(tx):
    query = (
        "MATCH ()-[r]->() "
        "WHERE r.name = ':defines' "
        "SET r.`cidoc-crm_relationship` = 'P196' "
        "MATCH ()-[r]->() "
        "WHERE r.name = ':has_title' "
        "SET r.`cidoc-crm_relationship` = 'P102' "
        "MATCH ()-[r]->() "
        "WHERE r.name = 'http://dbpedia.org/ontology/wikiPageWikiLink' OR r.name = ':is_about' "
        "SET r.`cidoc-crm_relationship` = 'P67' "
        "MATCH ()-[r]->() "
        "WHERE r.name = ':contains' "
        "SET r.`cidoc-crm_relationship` = 'P172' "
        "MATCH ()-[r]->() "
        "WHERE r.name = ':shows_features_of' "
        "SET r.`cidoc-crm_relationship` = 'P130'"
    )
    tx.run(query)


def assign_cidoc_crm_entities(tx):
    query = (
        "MATCH (e) "
        "WHERE e.type = 'cultobj' "
        "SET e.`cidoc-crm` = 'E19' "
        "MATCH (e) "
        "WHERE e.type = 'place' "
        "SET e.`cidoc-crm` = 'E53' "
        "MATCH (e) "
        "WHERE e.type = 'descr' OR e.type = 'title' "
        "SET e.`cidoc-crm` = 'E90'"
    )
    tx.run(query)

def add_labels_from_properties(tx):
    query = """
    MATCH (n)
    WHERE n.label IS NOT NULL OR n.name IS NOT NULL
    WITH n, 
         CASE 
           WHEN n.label IS NOT NULL THEN toString(n.label)
           ELSE toString(n.name)
         END AS newLabel
    WHERE newLabel IS NOT NULL AND size(newLabel) > 0
    CALL apoc.create.setLabels(n, [newLabel]) YIELD node
    RETURN count(DISTINCT node) AS NodesLabeled
    """
    tx.run(query)

def merge_sameLabels_nodes(tx):
    query = """
    MATCH (n)
    WHERE n.label IS NOT NULL OR n.name IS NOT NULL
    WITH n, 
         CASE 
           WHEN n.label IS NOT NULL THEN toString(n.label)
           ELSE toString(n.name)
         END AS newLabel
    WHERE newLabel IS NOT NULL AND size(newLabel) > 0
    CALL apoc.create.setLabels(n, [newLabel]) YIELD node
    WITH DISTINCT newLabel

    MATCH (n)
    WHERE newLabel in labels(n)
    WITH newLabel, collect(n) AS nodes
    WHERE size(nodes) > 1
    CALL apoc.refactor.mergeNodes(nodes, {properties: "combine", mergeRels: true})
    YIELD node as mergedNode
    RETURN count(mergedNode) as MergedNodeCount, collect(mergedNode.label) as MergedLabels
    """
    tx.run(query)

# Example usage with a Neo4j driver:
# from neo4j import GraphDatabase

# driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# with driver.session() as session:
#     nodes_labeled = session.write_transaction(add_labels_from_properties)
#     print(f"Number of nodes labeled: {nodes_labeled}")

# driver.close()

def merge_sameName_nodes(tx):
    query = """
    MATCH (n)
    WHERE n.name IS NOT NULL
    WITH n.name AS name, collect(n) AS nodes
    // Only process names where there's more than one node
    WHERE size(nodes) > 1
    // Merge the nodes
    CALL apoc.refactor.mergeNodes(nodes, {properties: "combine", mergeRels: true})
    YIELD node as mergedNode
    // Return the results
    RETURN count(mergedNode) as MergedNodeCount, collect(mergedNode.name) as MergedNodeNames
    """
    tx.run(query)

def export_graph_as_json(tx):
    
    query = """
    CALL apoc.export.json.all(null, {stream: true})
    YIELD data
    RETURN data
    """
    result = tx.run(query)
    return result.single()['data']

def export_graph_as_csv(tx):

    query = """
    CALL apoc.export.csv.all(null, {stream: true})
    YIELD data
    RETURN data
    """
    result = tx.run(query)
    return result.single()['data']



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
     
#MERGE (a:LabelA {name: 'NodeName'})
#MERGE (b:LabelB {name: 'NodeName'})
#WITH a, b
#WHERE id(a) <> id(b)  // Ensure we're not merging the same node with itself
#CALL apoc.refactor.mergeNodes([a, b]) YIELD node
#RETURN node

#Momentarily, KGs are at disposal only in Turtle Format

def importKnowledgebase(self, datapath):
    with open(datapath, 'r') as file:
        if datapath[0] != "h":
            datapath = "file:///" + datapath.replace("\\", "/")
        if datapath[-3:] == "csv":
            query = ("LOAD CSV WITH HEADERS FROM '" + str(datapath) +"' as row "
                       " MERGE (nodeA:cultobj {value: row.cultobj})"
                       " MERGE (nodeB:title {value: row.title})"
                       " MERGE (nodeC:museum {value: row.museo})"
                       " MERGE (nodeD:descr {value: row.descr})"
                       " MERGE (nodeA)-[P102:has_title]->(nodeB)"
                       " MERGE (nodeD)-[P196:defines]->(nodeA)"
                       " MERGE (nodeC)-[P172:contains]->(nodeA)"
                       " MERGE (nodeA)-[P129:is_about]->(nodeD)"
                       )
            #query = ("LOAD CSV WITH HEADERS FROM '" + str(datapath) +"' AS row CREATE (:Object {cultobj: row.cultobj, title: row.title,  museum: row.museo,  description: row.descr});")
        else: #we suppose that the available fromats are only csv and ttl. This option captures also the case of a uri ending in ".git"
            query = ("CALL n10s.rdf.import.fetch(\"" + str(datapath) +"\",\"Turtle\");") # {{handleVocabUris: 'IGNORE', handleMultival: 'ARRAY', commitSize: 500, nodeCacheSize: 200000}})
        for record in self.run(query, datapath=datapath):
            print(record)

# driver = GraphDatabase.driver("bolt://localhost:7687",
#                               auth=("neo4j","***")) 
# with driver.session(database="europeana") as session:
#     session.execute_write(importKnowledgebase, "C:\\Users\\Palma\\Downloads\\2048714_Ag_EU_3D-ICONS_ITABC.csv")


def load_merged_knowledgebase(tx, file_path):
    query = (
        "LOAD CSV WITH HEADERS FROM $file_path AS row "
        "WITH row WHERE row.entity1 IS NOT NULL "
        "MERGE (e1:Entity {name: row.entity1}) "
        "WITH row WHERE row.mid1 IS NOT NULL "
        "MERGE (mid1:Entity {name: row.mid1}) "
        "WITH row WHERE row.mid2 IS NOT NULL "
        "MERGE (mid2:Entity {name: row.mid2}) "
        "WITH row WHERE row.mid3 IS NOT NULL "
        "MERGE (mid3:Entity {name: row.mid3}) "
        "WITH row WHERE row.entity2_dbpedia IS NOT NULL "
        "MERGE (e2_dbpedia:Entity {name: row.entity2_dbpedia}) "
        "WITH row WHERE row.entity2_arco IS NOT NULL "
        "MERGE (e2_arco:Entity {name: row.entity2_arco}) "
        "WITH row WHERE row.entity1 IS NOT NULL AND row.mid1 IS NOT NULL AND row.pf1 IS NOT NULL "
        "MATCH (e1:Entity {name: row.entity1}), (mid1:Entity {name: row.mid1}) "
        "MERGE (e1)-[:RELATION {name: row.pf1}]->(mid1) "
        "WITH row WHERE row.mid1 IS NOT NULL AND row.mid2 IS NOT NULL AND row.pf2 IS NOT NULL "
        "MATCH (mid1:Entity {name: row.mid1}), (mid2:Entity {name: row.mid2}) "
        "MERGE (mid1)-[:RELATION {name: row.pf2}]->(mid2) "
        "WITH row WHERE row.mid2 IS NOT NULL AND row.mid3 IS NOT NULL AND row.pf3 IS NOT NULL "
        "MATCH (mid2:Entity {name: row.mid2}), (mid3:Entity {name: row.mid3}) "
        "MERGE (mid2)-[:RELATION {name: row.pf3}]->(mid3) "
        "WITH row WHERE row.mid3 IS NOT NULL AND row.entity2_dbpedia IS NOT NULL AND row.pf4 IS NOT NULL "
        "MATCH (mid3:Entity {name: row.mid3}), (e2_dbpedia:Entity {name: row.entity2_dbpedia}) "
        "MERGE (mid3)-[:RELATION {name: row.pf4}]->(e2_dbpedia) "
        "WITH row WHERE row.entity1 IS NOT NULL AND row.entity2_arco IS NOT NULL AND row.relationship IS NOT NULL "
        "MATCH (e1:Entity {name: row.entity1}), (e2_arco:Entity {name: row.entity2_arco}) "
        "MERGE (e1)-[:RELATION {name: row.relationship}]->(e2_arco)"
    )
    tx.run(query, file_path=file_path)
