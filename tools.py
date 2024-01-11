import wikipediaapi as wa
import requests
from bs4 import BeautifulSoup
from collections import deque
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

# Depth-First Search (DFS) to find the shortest path
def dfs(current_article, path, visited, depth):
    if depth > max_depth:
        return None

    visited.add(current_article)
    path.append(current_article)

    if current_article == end_article:
        return path

    for link in get_links(current_article):
        if link not in visited:
            result = dfs(link, path.copy(), visited, depth + 1)
            if result:
                return result

    return None

def enttype(text):
    # Load the English language model
    nlp = spacy.load("en_core_web_sm")

    # Process the text with spaCy
    doc = nlp(text)

    # Extract entities and their types
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print = ""
    for entity, entity_type in entities:
        print = f"Entity: {entity}, Type: {entity_type}"
    print(print)
    return print

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
    api_key = "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"
    openai.api_key = api_key

    response = openai.Completion.create(
        engine="davinci",  #text-davinci-003
        prompt=user_question,
        max_tokens=50  
    )
    print(response.choices[0].text.strip())