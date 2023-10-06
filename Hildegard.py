from neo4j import GraphDatabase
import DBManipulation as gm
import DBPSpotlight  as dbs
import KGAlignmentpy as kga
import wikifier as w
import tools as t
import EntityTyping as et
import ImportDataset  as id
from SPARQLWrapper import SPARQLWrapper, JSON
import sdowmock as sdow

#creare grafo di conoscenza a partire da dataset sui beni culturali
    # trovare collegamenti interni 
    # stabilire link tra oggetti correlati
    # una volta creato il KG procedere alla pubblicazione
    # La parte CRUD é lasciata a un altro articolo e a un altro momento dello sviluppo dell´algoritmo

#Inserire caso in cui il numero di seed non é conosciuto in partenza
#Inserire scenario in cui il dataset non sia ancora stato definito:
#Do you already dispose of a KB?
#IF yes, proceed as in the following code
#IF no, create it. how?

#CASE 1:  one seed
# KB preliminary linking
# Trovare tutte le occorrenze nel dataset a disposizione
# Entity linking sulle descrizioni.
# Relationship extraction
# Short-path algorithm su tutte le possibili permutazioni delle doppiette

#CASE 2: two seeds

#CASE 3: More seeds.


# Example usage:
#start_page = "https://en.wikipedia.org/wiki/Alexander_the_Great"
#end_page = "https://en.wikipedia.org/wiki/Antonino_Cannavacciuolo"
#shortest_path = wsp.find_shortest_path(start_page, end_page)
#print(shortest_path)
#print(wsp.get_links("https://en.wikipedia.org/wiki/Alexander_the_Great"))

# Perform DFS to find the shortest path
#visited = set()
#path = dfs(start_article, [], visited, 0)

#if path:
#   print(path)
#else:
#   print(None)

# Example usage
# Define the SPARQL query


#id.fetchSPARQLendpoint("museum", "arco", "it")
start_entity = "Barack_Obama"
end_entity = "Albert_Einstein"
start = "Battle_of_Issus"
end = "Trier"

#shortest_path = sp.shortest_path_between_entities(start_entity, end_entity)
#shortest_path = sp.DBpedia_short_path(start_entity, end_entity)
#shortest_path = sp.retrieve_common_entities(start, end)
sdow.related_entities_triples(start, end)
#if shortest_path:
#    print(f"Shortest path from {start_entity} to {end_entity}:")
#    print(" -> ".join(shortest_path))
#else:
#    print(f"No path found from {start_entity} to {end_entity}")

driver = GraphDatabase.driver("neo4j://localhost:7687",
                              auth=("neo4j","pipi1233")) 

with driver.session(database="neo4j") as session:
    #print("How many seeds do you want to start your search with? (Please type the integer digit) \n"
    #      +"Con quanti semi vuoi cominciare la tua ricerca (prego inserire un numero da uno a dieci): \n")

    while True:
        try:
            kb =     input("Welcome to Hildegard, a tool for linking and enrich heritage objects contained in a specific site. Have you already"
          + "uploaded your knowledge base to Neo4J? (y/n) \n")
            if kb == "y" or kb == "n":
                # Valid input
                break
            else:
                print("Invalid input. Please type y or n.\n"
                        +"Input non valido. Prego inserire \"y\" per \"si\" e \"n\" per \"no\"\n")
        except Exception as e:
            print(f"An error occurred: {e}")
    if kb == "n":
        # for simplicity, this part is momentarily limited to the arco endpoint and the italian language
        # try-except loops to catch input mistakes are also momentarily allowed
        space = input("From which italian region would you like to start your search?") 
        endpoint = input("From which knowledge base would like to fetch your dataset? Type 'wikipedia', 'europeana', 'arco', or 'yago': \n") 
        lang = input("In which language do you want the results to be shown? Type the language code according to the ISO 639-1: \n") #multilinguality
        id.fetchSPARQLendpoint(text, endpoint, lang)
        if space == "region":
            id.fetchSPARQLendpoint("museum", endpoint, lang)
    while True:
        try:
            seed = input("Con quanti semi vuoi cominciare la tua ricerca (prego inserire un numero): \n")
            if seed.isdigit():
                # Valid input: a single-digit integer
                break
            else:
                print("How many seeds do you want to start your search with? (Please type the integer digit) \n"
          +"Invalid input. Please type a single-digit integer.\n"
                      +"Input non valido. Prego inserire un numero \n")
        except Exception as e:
            print(f"An error occurred: {e}")
    seed = int(seed)
    seeds=seed
    while seeds>0: 
        keyword = input("Inserisci un termine che vuoi trovare nel grafo di conoscenza \n"+"Insert the name you want to find in the knowledge graph: \n")
        session.execute_read(gm.find_related, keyword)
        seeds = seeds - 1
    #session.execute_read(gm.find_related_key, input("Insert the name you want to find in the knowledge graph \n"))
    seeds = seed
    descr = ""
    while seeds>0: 
        #in the final implementation of this app, the description extraction will occurr by direct node selection
        #from the user through the web interface
        element_id = input("Insert the titles of heritage objects from whose descriptions you want to extract, type and link enitities \n"
                              + " Inserire i titoli degli oggetti culturali dei quali vuoi estrarre, annotare e collegare le entitá: \n")
        
        session.execute_read(gm.find_related_descr, element_id)
        descri = input("Inserisci porzione di testo su cui vuoi eseguire entity extraction e linking in seguito.")
        descr = descr + " " + descri
        seeds = seeds - 1
    #et.enttype(descr)
    #dbs.entitylinking(descr)
    w.CallWikifier(descr)
    start_article = input("Insert the wikipedia entry from which you want your search to start:/n")
    end_article = input("Insert the wikipedia entry from which you want your search to end:/n")
    max_depth = input("Insert search maximal depth:")
    shortest_path = wsp.find_shortest_path(start_article, end_article)
    if shortest_path:
        print("Shortest path between {} and {}: ".format(start_article, end_article))
        for article in shortest_path:
            print(article)
    else:
        print("No path found between {} and {} within {} degrees.".format(start_article, end_article, max_depth))
    driver.close()
