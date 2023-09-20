from neo4j import GraphDatabase
import DBManipulation as gm
import DBPSpotlight  as dbs
import KGAlignmentpy as kga

#creare grafo di conoscenza a partire da dataset
    # trovare collegamenti interni 
    # stabilire link tra oggetti correlati
    # 


driver = GraphDatabase.driver("neo4j://localhost:7687",
                              auth=("neo4j","pipi1233"))

with driver.session(database="neo4j") as session:
    session.execute_read(gm.find_related, input("Insert the name you want to find in the knowledge graph \n"))
    #session.execute_read(gm.find_related_key, input("Insert the name you want to find in the knowledge graph \n"))
    descr = input()
    dbs.entitylinking(descr)
driver.close()
