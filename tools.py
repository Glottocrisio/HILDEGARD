import wikipediaapi as wa
import requests
from bs4 import BeautifulSoup
from collections import deque, defaultdict
from SPARQLWrapper import SPARQLWrapper, JSON
import re
import spacy
import urllib.parse, urllib.request, json
from itertools import combinations
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS
import mediawikiapi as mwa
import pywikigraph as wgr
import wikipedia as w
from wikidata.client import Client
import json
import csv
import pandas as pd
import os
import ast
import openai
import time
import json
import argparse


cidoc_class_mapping = {
    "E2": "Temporal Entity",
    "E4": "Period",
    "E5": "Event",
    "E18": "Physical Thing",
    "E19": "Physical Object",
    "E21": "Person",
    "E27": "Site",
    "E29": "Design or Procedure",
    "E39": "Actor",
    "E53": "Place",
    "E57": "Material",
    "E67": "Birth"
}


cidoc_property_mapping = {
    "P2": "has type",
    "P4": "has time-span",
    "P5": "consist of",
    "P7": "took place at",
    "P10": "falls within",
    "P14": "carried out by",
    "P15": "was influenced by",
    "P20": "had specific purpose",
    "P53": "has former or current location",
    "P67": "refers to",
    "P69": "is associated with",
    "P94": "has created",
    "P96": "by mother",
    "P97": "from father",
    "P102": "has title",
    "P103": "was intended for",
    "P104": "is subject to",
    "P106": "is composed of",
    "P124": "transformed",
    "P126": "employed",
    "P129": "is about",
    "P130": "shows features of",
    "P132": "spatiotemporally overlaps with",
    "P138": "represents",
    "P148": "has component",
    "P165": "incorporates (is incorporated in)",
    "P172": "contains",
    "P190": "has symbolic content",
    "P196": "defines"
}

sparql = SPARQLWrapper("http://dbpedia.org/sparql")



def json2csv(input_json, output_csv):

    with open(input_json, 'r') as json_file:
        fil = json_file.read()
        fil = fil.replace("\\","")
        i = 0
        json_acceptable_string = ""
        while i < len(fil):
            if fil[i] == "'" and (fil[i-2] == "," or fil[i-2] == ":" or fil[i-2] == "}" or fil[i+1] == "," or fil[i+1] == ":" or fil[i+1] == ":" or fil[i+1] == "}" or fil[i+1] == "]" or fil[i-1] == ":" or fil[i-1] == "{" or fil[i-1] == "["):
                json_acceptable_string += fil[i].replace("\'","\"")
            elif fil[i]== "\"":
                if fil[i-2]== ":" or fil[i+1] == "}":
                    json_acceptable_string += fil[i]
                else:
                    json_acceptable_string += fil[i].replace("\"","")
            else:
                json_acceptable_string += fil[i]
            i+=1
                

   
    if os.path.exists("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\sanitized"+input_json.replace(".json","").replace("C:\\Users\\Palma\\Desktop\\PHD\\DatasetThesis\\HildegardData\\","")+".json") == False or os.path.getsize("C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\sanitized"+input_json.replace(".json","").replace("C:\\Users\\Palma\\Desktop\\PHD\\DatasetThesis\\HildegardData\\","")+".json")==0:
        with open(input_json.replace(".json","")+"sanitized.json", "w") as s_json_file:
            s_json_file.write(str(json_acceptable_string))
    
    
    with open(input_json.replace(".json","")+"sanitized.json", "r") as s_json_file:
        data = json.load(s_json_file)

    # Extract headers from JSON keys (assuming all items have the same structure)
    headers = list(data['head']['vars'])
    with open('C:\\Users\\Palma\\.Neo4jDesktop\\relate-data\\dbmss\\dbms-3f4078ad-d08d-4625-b967-c1e0ee8a2a81\\import\\'+output_csv, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        values = []
        list_dicto = []
        for d in data['results']['bindings']:
            for header in d:
                values.append(d[str(header)]['value'])
        while len(values)>0:
            dicto = {}
            dicto = dict(zip(headers, values))
            list_dicto.append(dicto)
            values = values[len(headers):]
        writer.writerows(list_dicto)


def csv2json(input_csv, output_json):
    data = []
    with open(input_csv, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data.append(row)

    with open(output_json, 'w') as json_file:
        json.dump(data, json_file, indent=4)


#Takes as input a text file with the extracted triples and returns the triple harmonized with our model

def harmonize_triples2crm(input_filepath, output_filename):
    harmonizedtriples = []
    inputtriples = []
    prev_title = None
    

    with open(input_filepath, "r") as f:
        inputtriples = f.read()
        inputtriples = inputtriples.replace("[","").replace("]","")
        i = 0
        batch_triples = ""
        while i < len(inputtriples):
            batch_triples += inputtriples[i]
            if inputtriples[i] == ')' and i + 1 < len(inputtriples) and inputtriples[i + 1] == ',':
                batch_triples += ';'
                i += 1
            i += 1

        list_inputtriples = batch_triples.split(';')
        f.close()

    s_triples = ""
    inputtriples = ''.join(list_inputtriples)
    i = 0
    while i < len(inputtriples):
        s_triples += inputtriples[i]
        if (inputtriples[i] == '}' and i + 1 < len(inputtriples) and inputtriples[i + 1] == ',') or (inputtriples[i] == ')' and i + 1 < len(inputtriples) and inputtriples[i + 2] == '('):
            s_triples = s_triples + ';'
            i += 1
        i += 1
    s_triples = s_triples.replace("(","").replace(")","")
    list_input_striples = s_triples.split(';')

    for idx, triple in enumerate(list_input_striples):
        try:
            if idx == 0:
                triplet = ast.literal_eval(triple)
            else:
                triple = triple[1:]
                triplet = ast.literal_eval(triple)
            title = triplet['title']
            caption = triplet['caption']
            href = triplet['href']
            
        
            current_triple = {
                'title': title,
                'cidoc-relation': 'P104',
                'descr': caption
            }
            harmonizedtriples.append(current_triple)
            harmonizedtriples.append({
                    'descr': caption,
                    'cidoc-relation': 'P196',
                    'uri': href
                })
        
            harmonizedtriples.append({
                'uri': href,
                'cidoc-relation': 'P102',
                'title': title
            })

            harmonizedtriples.append({
                'descr': caption,
                'cidoc-relation': 'P196',
                'title': title
            })
        
            harmonizedtriples.append({
                'title': title,
                'cidoc-relation': 'P104',
                'descr': caption
            })

            harmonizedtriples.append({
                'uri': href,
                'cidoc-relation': 'P67',
                'descr': caption
            })

            harmonizedtriples.append({
                'title': title,
                'cidoc-relation': 'P67',
                'uri': href
            })

            if idx > 0:
                try:
                    p_idx = int(idx)-1
                    prev_triple = ast.literal_eval(str(list_input_striples[p_idx])[1:])
                    prev_title = prev_triple['title']
                    if prev_title != title and prev_title != None:
                        harmonizedtriples.append({
                            'prev_title': prev_title,
                            'cidoc-relation': 'P67',
                            'title': title
                        })
                    prev_triple = None
                except Exception as e:
                    pass 
        except Exception as e:
            pass 
    with open(f"C:\\Users\\Palma\\Desktop\\PHD\\HILD&GARD\\{output_filename}harmonizedtriples.txt", "w") as o:
        o.write(str(harmonizedtriples))
        o.close()

    return harmonizedtriples



def get_dbpedia_uri_lang(entity, lang = "it"):
    wikidat = SPARQLWrapper("https://query.wikidata.org/sparql")
    try:
        query = """
            PREFIX wd: <http://www.wikidata.org/entity/>
            SELECT DISTINCT ?qid
            WHERE {
              BIND(STRLANG(\"""" + entity + """\", "en") AS ?label ) .
              ?item rdfs:label ?label .
              BIND(STRAFTER(STR(?item), STR(wd:)) AS ?qid) .
            }

            LIMIT 1
        """
        wikidat.setQuery(query)
        wikidat.setReturnFormat(JSON)
        results = wikidat.queryAndConvert()
        result = results['results']['bindings'][0]['qid']['value']
    except Exception as e:
        pass
    try:
        queryy = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX wd: <http://www.wikidata.org/entity/> 
            SELECT  *
            WHERE {
                    wd:""" + result + """ rdfs:label ?label .
                    FILTER (langMatches( lang(?label), \"""" + lang + """\" ) )
                  } 
            LIMIT 1
        """
          
        wikidat.setQuery(queryy)
        wikidat.setReturnFormat(JSON)
        resultss = wikidat.queryAndConvert()
        resul = resultss['results']['bindings'][0]['label']['value']
        uri = 'https://'+ str(lang)+ '.dbpedia.org/page/' + str(resul)
        response = requests.get(uri)
        return uri

    except Exception as e:
        response = requests.get("https://dbpedia.org/page/" + str(entity))
        soup = BeautifulSoup(response.content, "html.parser")
        text = str(soup.text)
        text_list = text.split("\n")
        text_list = [x for x in text_list if x != '']
        wikicommons = []
        dbr = []
        lang_list = []

        for line in text_list:
            #if substring of href == lang THEN assign to the variable 'uri' the value of 'href'
            if line[-4:] == "("+ str(lang) + ")":
                line = line[:-4]
                lang_list.append(line)
            if line[:12] == "wiki-commons":
                wikicommons.append(line)
            if line[:3] == "dbr":
                dbr.append(line)

        if len(lang_list) and len(wikicommons) and len(dbr) > 0: 
            with open(f"C:\\Users\\Palma\\Desktop\\PHD\\DatasetThesis\\HildegardData\\{entity}{lang}wikimediacommons.txt", "a") as f:
                for x in wikicommons:
                    try:
                      f.write(str(x) + "\n")
                    except Exception as e:
                        pass
                f.close()

            with open(f"C:\\Users\\Palma\\Desktop\\PHD\\DatasetThesis\\HildegardData\\{entity}{lang}dbpediaresources.txt", "a") as g:
                for x in dbr:
                    try:
                        g.write(str(x) + "\n")
                    except Exception as e:
                        pass
                g.close()

            i = 0
            lang_list.reverse()
            uri = ""
            while i < 2:
                try:
                    get_uri = requests.get("https://" + str(lang)+ ".dbpedia.org/page/" + str(lang_list[i]))
                    uri = "https://" + str(lang)+ ".dbpedia.org/page/" + str(lang_list[i])
                except Exception as e:
                    i = i + 1
                #uri = "https://" + str(lang)+ ".dbpedia.org/resource/" + str(lang_list[i])
            if uri == "":
                uri = "https://yago-knowledge.org/graph/" + str(entity)
                #print(uri)
                return uri


      
def entitylinking_dbspot(text):
    url ="https://api.dbpedia-spotlight.org/en/annotate"
    headers={'accept':'application/json'}

    resp = requests.get(url, headers=headers, params={"text": text})
     
    data = resp.json()
    print(data)
    return data

def get_dbpedia_uri_italian(wikipedia_entity_english):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
        PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?italianURI
        WHERE {{
          ?englishURI rdfs:label {wikipedia_entity_english}@en .
          ?englishURI dbpedia-owl:wikiPageWikiLink ?italianURI .
          FILTER (LANG(?italianURI) = "it")
        }}
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    links = []
    for result in results["results"]["bindings"]:
        linked_resource = result["linkedResource"]["value"]
        if linked_resource.startswith("http://dbpedia.org/resource/"):
            link = linked_resource.split("/resource/")[1]
            links.append(link)

    query_url = f"https://api.dbpedia-spotlight.org/en/annotate?text={wikipedia_uri_english}&confidence=0.3"

    response = requests.get(query_url)

    response_json = response.json()

    dbpedia_uri_italian = None
    for annotation in response_json["annotations"]:
        if annotation["@type"] == "DBpediaSpotlight:Entity" and annotation["dbpediaURI"].endswith("/it"):
            dbpedia_uri_italian = annotation["dbpediaURI"]
            break

    return dbpedia_uri_italian


#it works
def retrieve_common_entities(start, end):
    sparql.setQuery(f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT DISTINCT ?relatedEntity
    WHERE {{
      <http://dbpedia.org/resource/{start}> ?p ?relatedEntity .
      ?relatedEntity ?q <http://dbpedia.org/resource/{end}> .
        }}
        """
        )
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    return results

def get_dbpedia_relationships(entity1, entity2, filter=False):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT * WHERE {{
          dbr:{entity1} ?pf1 ?of1 .
          ?of1 ?pf2 ?c .
          dbr:{entity2} ?ps1 ?os1 .
          ?os1 ?ps2 ?c .
          """
    if filter:
        query += f"""
          
        }} LIMIT 50
        """
    else:
        query +=  f"""
            FILTER (?pf2 NOT IN (dbo:Person, dbo:wikiPageWikiLink, owl:Thing))
            FILTER (?pf1 NOT IN (dbo:Person, dbo:wikiPageWikiLink, owl:Thing))
            FILTER (?ps2 NOT IN (dbo:Person, dbo:wikiPageWikiLink, owl:Thing))
            FILTER (?ps1 NOT IN (dbo:Person, dbo:wikiPageWikiLink, owl:Thing))
            FILTER (?c NOT IN (dbo:Person, dbo:wikiPageWikiLink, owl:Thing))
        }} LIMIT 50
        """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

def get_direct_neighbors(entity):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(f"""
        SELECT DISTINCT ?neighbor
        WHERE {{
            {{
                <http://dbpedia.org/resource/{entity}> ?p ?neighbor
            }}
            UNION
            {{
                ?neighbor ?p <http://dbpedia.org/resource/{entity}>
            }}
        }}
    """)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    neighbors = []
    for result in results["results"]["bindings"]:
        neighbor_uri = result["neighbor"]["value"]
        if "/resource/" in neighbor_uri:
            neighbor = neighbor_uri.split("/resource/")[1]
            neighbors.append(neighbor)

    return neighbors

# Function to find the shortest path between two entities
def shortest_path_between_entities(start_entity, end_entity):
    visited = set()
    queue = [(start_entity, [start_entity])]

    while queue:
        current_entity, path = queue.pop(0)
        visited.add(current_entity)

        if current_entity == end_entity:
            return path

        neighbors = get_direct_neighbors(current_entity)
        for neighbor in neighbors:
            if neighbor not in visited:
                new_path = path + [neighbor]
                queue.append((neighbor, new_path))

    return None

# Function to fetch links from a DBpedia page
def get_links_from_dbpedia(dbpedia_link):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(f"""
        SELECT ?linkedResource
        WHERE {{
            <http://dbpedia.org/resource/{dbpedia_link}> ?p ?linkedResource
        }}
    """)
    sparql.setReturnFormat(JSON)
    
    results = sparql.query().convert()
    
    links = []
    for result in results["results"]["bindings"]:
        linked_resource = result["linkedResource"]["value"]
        if linked_resource.startswith("http://dbpedia.org/resource/"):
            link = linked_resource.split("/resource/")[1]
            links.append(link)
    
    return links


# Function to find the shortest path between two Wikipedia articles using BFS
def find_shortest_path(start_article, end_article, max_depth=6):
    wiki_wiki = wa.Wikipedia('HILDE&GARD/1.0 (your@email.com)', 'en')

    queue = [(start_article, [start_article])]

    while queue:
        current_article, path = queue.pop(0)

        if current_article == end_article:
            return path
        if len(path) < max_depth:
            page = wiki_wiki.page(current_article)
            links = [link.title for link in page.links]
            for link in links:
                if link not in path:
                    queue.append((link, path + [link]))

    return None

# Create a function to get links from an article
def get_wikilinks(article_title):
    wiki_wiki = wa.Wikipedia('HILDE&GARD/1.0 (your@email.com)', 'en')
    page = wiki_wiki.page(article_title)
    return [link.title for link in page.links]

# def enttype(text):
#     # Load the English language model
#     nlp = spacy.load("en_core_web_sm")

#     # Process the text with spaCy
#     doc = nlp(text)

#     # Extract entities and their types
#     entities = [(ent.text, ent.label_) for ent in doc.ents]
#     print = ""
#     for entity, entity_type in entities:
#         print = f"Entity: {entity}, Type: {entity_type}"
#     print(print)
#     return print

def text2list(filename, delimiter=","):
    try:
      with open(filename, "r") as f:
        contents = f.read()
    except Exception as e:
        with open(filename + ".txt", "r") as f:
            contents = f.read()
    elements = contents.split(delimiter)
    del elements[-1]
    return elements


def get_combos(elements):
  seen_couplets = set()
  couplets = []
  for i in range(len(elements)):
    for j in range(i + 1, len(elements)):
      if elements[i] != elements[j] and (elements[i], elements[j]) not in seen_couplets:
        couplets.append((elements[i], elements[j]))
        seen_couplets.add((elements[i], elements[j]))
  return couplets

def llm(user_question):
    api_key = "***"
    openai.api_key = api_key

    response = openai.Completion.create(
        engine="davinci",  #text-davinci-003
        prompt=user_question,
        max_tokens=50  
    )
    print(response.choices[0].text.strip())


import requests
import random

def get_links(title):
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "links",
        "pllimit": "max"
    }
    response = json.loads(requests.get(url, params=params).text)
    page = next(iter(response["query"]["pages"].values()))
    return [link["title"] for link in page.get("links", [])]

def clickstream_walk(start, end, max_steps=20):
    current = start
    path = [current]
    
    for _ in range(max_steps):
        if current == end:
            return path
        
        links = get_links(current)
        if end in links:
            path.append(end)
            return path
        
        next_page = random.choice(links)
        path.append(next_page)
        current = next_page
    
    return path + ["(Target not reached)"]

# # Example usage
# start_entity = "Anubis"
# end_entity = "Alexander the Great"

# result = clickstream_walk(start_entity, end_entity)
# print(" -> ".join(result))



def csv_to_json(csv_file_path, json_file_path, text_column):
    
    data = []

    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        if text_column not in csv_reader.fieldnames:
            raise ValueError(f"Column '{text_column}' not found in the CSV file.")
        
        for row in csv_reader:
            text = row[text_column].strip()
            
            if text:
                data.append({"text": text})

    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

    print(f"Successfully converted {len(data)} entries from CSV to JSON.")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Convert a column from a CSV file to a JSON file.")
#     parser.add_argument("csv_file", help="Path to the input CSV file")
#     parser.add_argument("json_file", help="Path to the output JSON file")
#     parser.add_argument("text_column", help="Name of the column containing the text to be extracted")

#     args = parser.parse_args()


def filter_json_by_length(input_file, output_file, min_length):
    # Read the input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filter the data
    filtered_data = [item for item in data if len(item['text']) >= min_length]
    
    # Write the filtered data to the output JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    
    print(f"Original number of texts: {len(data)}")
    print(f"Number of texts after filtering: {len(filtered_data)}")
    print(f"Filtered JSON saved to {output_file}")

#filter_json_by_length("test_data_entity_linking.json", "test_data_entity_linking_short.json", 100)
#csv_to_json("C:\\Users\\Palma\\Desktop\\PHD\\DatasetThesis\\HildegardData\\oggetticulturalimuseoarcheologiconapoliit.csv", "test_data_entity_linking.json", "descr")


def run_yago_query(entity, lang="it"):
    endpoint_url = "https://yago-knowledge.org/sparql/query"
    sparql = SPARQLWrapper(endpoint_url)

    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX yago: <http://yago-knowledge.org/resource/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT DISTINCT ?property ?value ?type ?parent ?wdparent ?ancestor ?wdancestor
                    ?description ?wikidataLink ?wikipediaLink ?image
                    ?subclass ?instance ?related
                    ?influenced ?influencedBy
    WHERE {{
      yago:{entity} ?property ?value.
      yago:{entity} rdf:type ?type.
      ?type rdfs:subClassOf* ?parent.
      ?parent rdfs:subClassOf ?ancestor.
      ?parent owl:sameAs ?wdparent.
      ?ancestor owl:sameAs ?wdancestor.
      
      OPTIONAL {{ yago:{entity} schema:description ?description. }}
      OPTIONAL {{ yago:{entity} owl:sameAs ?wikidataLink. 
                 FILTER(STRSTARTS(STR(?wikidataLink), "http://www.wikidata.org/entity/")) }}
      OPTIONAL {{ yago:{entity} schema:sameAs ?wikipediaLink. 
                 FILTER(STRSTARTS(STR(?wikipediaLink), "https://it.wikipedia.org/wiki/")) }}
      OPTIONAL {{ yago:{entity} schema:image ?image. }}
      OPTIONAL {{ ?subclass rdfs:subClassOf yago:{entity}. }}
      OPTIONAL {{ ?instance rdf:type yago:{entity}. }}
      OPTIONAL {{ yago:{entity} skos:related ?related. }}
      OPTIONAL {{ yago:{entity} dbo:influenced ?influenced. }}
      OPTIONAL {{ yago:{entity} dbo:influencedBy ?influencedBy. }}
      
      FILTER (LANG(?value) = "{lang}" || LANG(?value) = "")
      FILTER (?property != schema:mainEntityOfPage && ?property != schema:AlternateName)
    }}
    LIMIT 1000
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()

        entity_info = defaultdict(set)
        for result in results["results"]["bindings"]:
            for key, value in result.items():
                entity_info[key].add(value["value"])

        return entity_info

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None

def yago_write_results_to_file(entity, entity_info):
    output_file = f"{entity}_yago_info.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Information about {entity} in Italian.\n\n")
        for key, values in entity_info.items():
            f.write(f"{key.capitalize()}:\n")
            for value in values:
                f.write(f"  - {value}\n")
            f.write("\n")
    print(f"Results written to {output_file}")

def yago_query_and_save(entity):
    output_file = f"{entity}_yago_knowledge.txt"
    results = run_yago_query(entity)
    if results:
        yago_write_results_to_file(entity, results)
    else:
        print("No results to write.")


#yago_query_and_save("Alexander_the_Great")
#yago_query_and_save("Anubis")

def parse_input_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    data = {}
    current_key = None

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('Property:'):
            current_key = 'properties'
            data[current_key] = []
        elif line.startswith('Information'):
            current_key = 'entity_name'
            data[current_key] = []
        elif line.startswith('Value:'):
            current_key = 'values'
            data[current_key] = []
        elif line.startswith('Type:'):
            current_key = 'types'
            data[current_key] = []
        elif line.startswith('Parent:'):
            current_key = 'parents'
            data[current_key] = []
        elif line.startswith('Ancestor:'):
            current_key = 'ancestors'
            data[current_key] = []
        elif line and current_key:

            data[current_key].append(line.strip('- '))

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('Information'):
            data['entity_name']= line.replace('Information about ', '').replace(' (in Italian):', '')
            break

    return data

def generate_cypher_query(data):
    
    properties = {
        "label": next(v for v in data['values'] if not v.startswith("http")),
        "comment": next((v for v in data['values'] if v.startswith("fondatore") or len(v) > 50), ""),
        "image": next((v for v in data['values'] if v.startswith("http://commons.wikimedia.org")), ""),
        "birthDate": next((v for v in data['values'] if v.startswith("0")), ""),
        "deathDate" : "",
    }
    
    alternate_names = [v for v in data['values'] if v not in properties.values() and not v.startswith("http") and not v.startswith("0")]
    properties["deathDate"] = next((v for v in data['values'] if v.startswith("0") and v != properties["birthDate"]), "")
    types = data['types']
    ancestors = data.get('ancestors', [])
    entity_name = data['entity_name']

    query = f"""
    WITH {{
        name: "http://dbpedia.org/resource/{entity_name}",
        properties: {{
            label: "{properties['label']}",
            comment: "{properties['comment']}",
            image: "{properties['image']}",
            birthDate: "{properties['birthDate']}",
            deathDate: "{properties['deathDate']}"
        }},
        types: ["{types[0]}", "{types[1]}"],
        alternateNames: {alternate_names},
        ancestors: {ancestors}
    }} AS entityData

    MERGE (entity:`{{entityData.name}}` {{name: entityData.name}})
    SET entity += entityData.properties
    SET entity.cidoc_crm = "E21"
    SET entity.type = "Person"

    WITH entity, entityData
    UNWIND entityData.types AS typeName
    MERGE (type:`{{typeName}}` {{name: typeName}})
    SET type.cidoc_crm = "E55"
    MERGE (entity)-[r:`:has_type`]->(type)
    SET r.cidoc_crm_relationship = "P2"

    WITH entity, entityData
    UNWIND entityData.alternateNames AS altName
    MERGE (altNameNode:`{{altName}}` {{name: altName}})
    SET altNameNode.cidoc_crm = "E41"
    SET altNameNode.type = "Appellation"
    MERGE (entity)-[r:`:is_identified_by`]->(altNameNode)
    SET r.cidoc_crm_relationship = "P1"

    WITH entity, entityData
    UNWIND entityData.ancestors AS ancestor
    MERGE (ancestorNode:`{{ancestor}}` {{name: ancestor}})
    SET ancestorNode.cidoc_crm = "E55"
    MERGE (entity)-[r:`:has_broader_term`]->(ancestorNode)
    SET r.cidoc_crm_relationship = "P127"
    """
    print(query)
    return query

data = parse_input_file("Anubis_yago_info.txt")
generate_cypher_query(data)