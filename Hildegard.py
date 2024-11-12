from neo4j import GraphDatabase
import DBManipulation as gm
import wikifier as w
import tools as t
import importdataset  as id
from SPARQLWrapper import SPARQLWrapper, JSON
import sdowmock as sdow
#import metrics as metr
import os
from py2neo import Graph
from rdflib import Graph as RDFGraph
import re
import json


#creare grafo di conoscenza a partire da dataset sui beni culturali
    # trovare collegamenti interni 
    # stabilire link tra oggetti correlati
    # una volta creato il KG procedere alla pubblicazione (export in JSON)

#CASE 1:  one seed
# KB preliminary linking
# Trovare tutte le occorrenze nel dataset a disposizione
# Entity linking sulle descrizioni e titoli.
# Short-path algorithm su tutte le possibili combinazioni delle doppiette

#CASE 2: two seeds

#CASE 3: More seeds.

# langs = {'albanian':'als',
#             'arabic':'arb',
#             'bulgarian':'bul',
#             'chinese_simplified':'cmn',
#             'chinese_traditional':'qcn',
#             'danish':'dan',
#             'greek':'ell',
#             'english':'eng',
#             'persian':'fas',
#             'finnish':'fin',
#             'french':'fra',
#             'hebrew':'heb',
#             'croatian':'hrv',
#             'icelandic':'isl',
#             'italian':'ita',
#             'japanese':'jpn',
#             'catalan':'cat',
#             'basque':'eus',
#             'galicain':'glg',
#             'spanish':'spa',
#             'indonesian':'ind',
#             'malay':'zsm',
#             'dutch':'nld',
#             'polish':'pol',
#             'portuguese':'por',
#             'romanian':'ron',
#             'lithuanian':'lit',
#             'slovak':'slk',
#             'slovene':'slv',
#             'swedish':'swe',
#             'thai':'tha'}

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j","***")) 



with driver.session(database="dev") as session:


    while True:
        try:
            kb =     input("Benvenuto in Hildegard! Hai giá caricato la tua base di conoscenza in Neo4J? (y/n) \n" + 
                "Welcome to Hildegard, a tool for linking and enrich heritage objects contained in a specific site. Have you already uploaded your knowledge base to Neo4J? (y/n) \n")
            if kb == "y" or kb == "n":
                # Valid input
                break
            else:
                print("Invalid input. Please type y or n.\n"
                        +"Input non valido. Prego inserire \"y\" per \"si\" e \"n\" per \"no\"\n")
        except Exception as e:
            print(f"An error occurred: {e}")
    if kb == "n":
        while True:
            try:
                endpoint =  input("A quale SPARQL endpoint desideri connetterti?"
                + "Digita 'a' per 'ARCO', 'w' per 'Wikidata', 'y' per 'Yago', 'd' per 'DBpedia', 'e' per 'Europeana': \n"+ "Which SPARQL endpoint would you like to fetch?"
                + "Type 'a' for 'ARCO', 'w' for 'Wikidata', 'y' for 'Yago', 'd' for 'DBpedia', 'e' for 'Europeana': \n")
                if endpoint == "y" or endpoint == "a" or endpoint == "w" or endpoint == "d" or endpoint == "e":
                    # Valid input
                    break
                else:
                    print("Invalid input. Please type 'a', 'w', 'y', 'd' or 'e'.\n"
                            +"Input non valido. Prego inserire 'a', 'w', 'y', 'd' oppure 'e': \n")
            except Exception as e:
                print(f"An error occurred: {e}")
        
        while True:
            try:
                lang =     input("In quale lingua vuoi creare il grafo di conoscenza?"
                + "Digita 'en' per 'inglese' oppure 'it' per 'italiano' : \n" + "In which language would you like the Knowledge Graph be created?"
                + "Type 'en' for English or 'it' for Italian : \n")
                if lang == "en" or lang == "it":
                    # Valid input
                    break
                else:
                    print("Invalid input. Please type 'en' or 'it': \n"
                            +"Input non valido. Prego inserire 'en' or 'it': \n")
            except Exception as e:
                print(f"An error occurred: {e}")
        obj_list = []
        while True:
            try:
                seed = input("Con quanti semi vuoi cominciare la tua ricerca (prego inserire un numero): \n How many seeds would you like to start your query with? \n")
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
            obj_list.append(keyword)
            seeds = seeds - 1
        
        id.fetchSPARQLendpoint(endpoint, lang, obj_list)
        output_csv = input("Inserisci il nome del csv file \n"+"Insert the name of the .csv file: \n")
        t.json2csv(id.file_path_json_kb, output_csv)
        #kgdatapath = input("Please insert the path of the database file folder, if offline, or the uri where it is stored. In this case, provide the link of the github raw file")
        try:
            session.execute_write(gm.create_constraint)
            session.execute_write(gm.initialize_graph)
        except Exception as e:
            pass
        try:
            session.execute_write(gm.importKnowledgebase, output_csv)
            pass
        except Exception as e:
            pass
    else:
        while True:
            try:
                seed = input("How many seeds would you like to start your research with?\n Con quanti semi vuoi cominciare la tua ricerca (prego inserire un numero): \n")
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

        kg = ""
        while seeds>0: 
            keyword = input("Inserisci un termine che vuoi trovare nel grafo di conoscenza \n"+"Insert the name you want to find in the knowledge graph: \n")
            result = session.execute_read(gm.find_related, keyword)
            result_string = "\n".join([str(record) for record in result])
            kg = kg + result_string
            seeds = seeds - 1
        #session.execute_read(gm.find_related_key, input("Insert the name you want to find in the knowledge graph \n"))
        seeds = seed
        descr = ""
        
        #with open(f"C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\{keyword}shrinkeddataset.txt", "w", encoding='utf-8') as f:
        #    try:
        #      f.write(kg)
        #    except Exception as e:
        #        pass
        #    f.close()

        #current_file_name = f'{keyword}shrinkeddataset.txt'
        #new_file_name = f'{keyword}shrinkeddataset.ttl'

        #current_path = os.path.abspath(current_file_name)
        #new_path = os.path.abspath(new_file_name)

        #os.rename(current_path, new_path)
        #knowledgebase_importer = gm.KnowledgebaseImporter()
        
        #try:
    
        #    graph = Graph("neo4j://localhost:7687", auth=("dev","pipi1233"))

        #    # Read the Turtle file
        #    rdf_graph = RDFGraph()
        #    rdf_graph.parse(new_path, format="turtle")

        #    cypher_query = """
        #    CALL n10s.rdf.import.fetch("file://{file_path}", "{format}", {config})
        #    """

        #    format_params = {
        #        "file_path": new_path,
        #        "format": "Turtle",
        #        "config": {
        #            "handleVocabUris": "IGNORE",
        #            "handleMultival": "ARRAY",
        #            "commitSize": 500,
        #            "nodeCacheSize": 200000
        #        }
        #    }

        #    # Execute the Cypher query
        #    graph.run(cypher_query, **format_params)
        #except Exception as e:
            
        #    result = session.execute_write(gm.importKnowledgebase, new_path)
          
        #    # with this procedure the database is reduced to the entities which have been queried through the seeds

        #    print("Warning: the knowledge base file as SPARQL- queried from the original Datapoint will be modified by the following procedures: please save a copy before proceeding...")

        #    res = input("Do you want to create a Knowledge Graph based only on the input seeds?  (y/n) \n")
        #    if res == 'y':
        #        uris_list = []
        #        with open("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\Alessandro Magnoshrinkeddataset.ttl", "r", encoding='utf-8') as h:
        #            kg = h.read()
        #            pattern = re.compile(r'\'ns0__value\': \'([^\']+)\'') 
        #            matches = pattern.findall(kg)
        #            matches_str = ','.join(matches)
        #            result = session.execute_write(gm.delete, matches)
        #            h.close()
      
    element_id_list = []           
    while seeds>0: 
        #in the final implementation of this app, the description extraction will occurr by direct node selection
        #from the user through the web interface
        element_id = input("Insert the uri of heritage objects from whose descriptions you want to extract, type and link enitities \n"  + " Inserire l'uri degli oggetti culturali dei quali vuoi estrarre, annotare e collegare le entitá: \n\n")
        element_id_list.append(element_id)
        session.execute_read(gm.find_related_descr_json, element_id)
        descri = input("Inserisci porzione di testo su cui vuoi eseguire entity extraction e linking in seguito.\n\n")
        descr = descr + " " + descri
        seeds = seeds - 1
    #et.enttype(descr)
    #dbs.entitylinking(descr)
    w.CallWikifier(descr)
    while True:
        try:
            perm =     input("Do you want to retrieve entities connecting these entities in all possible combinations? (y/n) \n")
            if perm == "y" or perm == "n":
                # Valid input
                break
            else:
                print("Invalid input. Please type y or n.\n"
                        +"Input non valido. Prego inserire \"y\" per \"si\" e \"n\" per \"no\"\n")
        except Exception as e:
            print(f"An error occurred: {e}")
    if perm == "n":
        start_article = input("Insert the wikipedia entry from which you want your search to start:\n")
        end_article = input("Insert the wikipedia entry from which you want your search to end:\n")
        while True:
            try:
                lang =     input("In quale lingua vuoi creare il grafo di conoscenza?"
                + "Digita 'en' per 'inglese' oppure 'it' per 'italiano' : \n" + "In which language would you like the Knowledge Graph be created?"
                + "Type 'en' for English or 'it' for Italian : \n")
                if lang == "en" or lang == "it":
                    # Valid input
                    break
                else:
                    print("Invalid input. Please type 'en' or 'it': \n"
                            +"Input non valido. Prego inserire 'en' or 'it': \n")
            except Exception as e:
                print(f"An error occurred: {e}")
        sdow.related_entities(start_article, end_article)
        if lang == 'en' or lang == 'es' or lang == 'de' or lang == 'fr' or lang == 'ja':
            kgr = "dbpedia"
        else:
            kgr = "yago"
        sdow.related_entities_triples(start_article, end_article, kgr, lang)
    else:
        filename = input("Insert name of file where entities from wikification are stored \n")
        delimiter = ","

        elements = t.text2list(filename, delimiter)
        print(elements)
       
        combos = t.get_combos(elements)
        print(combos)

        for ele in combos:
            start_page = str(ele[0])
            end_page = str(ele[1])
            if lang == 'en' or lang == 'es' or lang == 'de' or lang == 'ja':
                kgr = "dbpedia"
            else:
                kgr = "yago"
            shortest_path = sdow.related_entities_triples(start_page, end_page, kgr)
            print(shortest_path)

    #while True:

    #    efile = input("Insert file name where all entities are stored: \n")
    #    dbpedia_uri_lang_list = []
    #    try:
    #        with open("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\" + str(efile), "r") as f:
    #                list_e = f.read()
    #                list_e = list_e.split(',')
    #                f.close()
    #    except Exception as e:
    #        print("File does not exists: please retry.")
            
    #    with open("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\" + str(efile), "r") as f:
    #            list_e = f.read()
    #            list_e = list_e.split(',')
    #            f.close()
    #    for e in list_e:
    #        dbpedia_uri_italian = t.get_dbpedia_uri_lang(e)
    #        if dbpedia_uri_italian:
    #            dbpedia_uri_lang_list.append(dbpedia_uri_italian)
    #            print(dbpedia_uri_italian)
    #        else:
    #            print("Could not find DBpedia URI in Italian for the given Wikipedia URI in English.")
    #            dbpedia_uri_lang_list.append("https://dbpedia.org/resource/" + str(e))
    #    with open("C:\\Users\\Palma\\Desktop\\PHD\\DatasetThesis\\HildegardData\\" + str(efile).replace(".txt","") + "italianuris.txt", "w") as f:
    #        for lang_uri in dbpedia_uri_lang_list:
    #            try:
    #                f.write(lang_uri + "\n")
    #            except Exception as e:
    #                pass
    #        f.close()
    #        break

    while True:
        try:
            triples = []
            res = input("Would you like to merge the retrieved triples in the original knowledge base?  (y/n): \n")
            
            if res=="y":
                select_triples_file = input("Insert the name of the file where the wikified triples are stored:")
                try:
                    triples_file = "C:\\Users\\Palma\\Desktop\\PHD\\DatasetThesis\\HildegardData\\" + str(select_triples_file)
                    h_triples = t.harmonize_triples2crm(triples_file, "h_triples_file")
                except Exception as e:
                    print("File does not exists: please retry.")
               
                    triples_file = input("Please insert the path of the file where all triples are stored: \n")#"C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\testharmonizedtriples.txt"  

            with open(triples_file, 'r') as file:
                fil = file.read()
                json_acceptable_string = fil.replace("'", "\"")
                file.close()
            with open(triples_file.replace(".txt","")+"jsond.txt", "w") as jsond:
                jsond.write(json_acceptable_string)
                jsond.close()
            with open(triples_file.replace(".txt","")+"jsond.txt", "r") as jsond:
                triples_data = json.load(jsond)

            for triple in triples_data:
                # Insert each triple into Neo4j
                try:
                    session.execute_write(gm.insert_triples, triple)
                except Exception as e:
                    pass
        except Exception as e:
            pass
        try:
            print("What entity class would you like to link?")
            for obj in t.cidoc_class_mapping:
                print(obj)
            class1 = input()
            key1 = [key for key, val in t.cidoc_class_mapping.items() if val == class1]
            print("To which entity class would you like to link it?")
            for obj in t.cidoc_class_mapping:
                print(obj)
            class2 = input()
            key2 = [key for key, val in t.cidoc_class_mapping.items() if val == class2]
            print("By which entity property would you like to link them?")
            for obj in t.cidoc_property_mapping:
                print(obj)
            rel = input()
            rell = [key for key, val in t.cidoc_property_mapping.items() if val == rel]
            session.execute_write(gm.create_link, rell, key1, key2)
        except Exception as e:
            pass

        for entity in elements:
            for elem in element_id_list:
                if entity in elem:
                   
                   session.execute_write(gm.create_link_json, elem, entity)

        session.execute_write(gm.link_similar_nodes, rell, entity, elem)
        session.write_transaction(gm.assign_entity_types)
        session.write_transaction(gm.assign_relationship_names)
        session.write_transaction(gm.remove_descr_type)
        session.write_transaction(gm.set_dbpedia_types)
        session.write_transaction(gm.set_cidoc_crm_relationships)
        session.write_transaction(gm.assign_cidoc_crm_entities)
        session.write_transaction(gm.link_museum2dbpedia)
        session.write_transaction(gm.add_labels_from_properties)
        session.write_transaction(gm.merge_sameLabels_nodes)
        session.write_transaction(gm.merge_sameName_nodes)
        session.write_transaction(gm.export_graph_as_json)
        session.write_transaction(gm.export_graph_as_csv)
        
    driver.close()
