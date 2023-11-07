import wikipediaapi as wa
import requests
from bs4 import BeautifulSoup
from collections import deque
from SPARQLWrapper import SPARQLWrapper, JSON
import re
import spacy
import urllib.parse, urllib.request, json
from itertools import combinations
from rdflib import Graph
import mediawikiapi as mwa
import pywikigraph as wgr
import wikipedia as w
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.by import By
#from selenium.webdriver.firefox.options import Options
from wikidata.client import Client


sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def get_dbpedia_uri_lang(entity, lang = "it"):
    #Find entity in wikidata using requests
    wikidat = SPARQLWrapper("https://query.wikidata.org/sparql")
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
        while i < len(lang_list):
            try:
                get_uri = requests.get("https://dbpedia.org/page/" + str(lang_list[i]))
                break
            except Exception as e:
                i = i + 1
                #get_uri = requests.get("https://dbpedia.org/page/" + str(lang_list[i]))
        uri = "https://dbpedia.org/page/" + str(lang_list[i])
        print(uri)
    return uri

def wikigraph_short_path(start, end):
    wg = wgr.WikiGraph()
    paths = wg.get_shortest_paths_info(start, end, directed = False)
    print(paths)
    return paths

def get_wikipedia_link_in_lang(english_wikipedia_link, lang):
    wiki_wiki = wa.Wikipedia('HILDE&GARD/1.0 (your@email.com)',lang)

    page_en = wiki_wiki.page(english_wikipedia_link)

    if page_en.exists():
        target_pages = page_en.langlinks
        for sprache in target_pages:
            if sprache == lang:
                print(sprache.fullurl)
                return sprache.fullurl
      
def entitylinking(text):
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

# Function to find the shortest path between two DBpedia links using BFS
#def shortest_path_between_dbpedia_links(start_link, end_link):
#    visited = set()
#    queue = deque([(start_link, [start_link])])

#    while queue:
#        current_link, path = queue.popleft()
#        visited.add(current_link)

#        if current_link == end_link:
#            return path

#        links = get_links_from_dbpedia(current_link)
#        for link in links:
#            if link not in visited:
#                new_path = path + [link]
#                queue.append((link, new_path))

#    return None



# Function to find the shortest path between two Wikipedia articles using BFS
def find_shortest_path(start_article, end_article, max_depth=6):
    # Use the custom session
    wiki_wiki = wa.Wikipedia('HILDE&GARD/1.0 (your@email.com)', 'en')

    # Initialize the BFS queue with the starting article
    queue = [(start_article, [start_article])]

    while queue:
        current_article, path = queue.pop(0)

        # Check if the current article is the target article
        if current_article == end_article:
            return path

        # Check if the depth is within the specified limit
        if len(path) < max_depth:
            page = wiki_wiki.page(current_article)
            links = [link.title for link in page.links]
            for link in links:
                if link not in path:
                    queue.append((link, path + [link]))

    # If no path is found within the specified depth, return None
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


def CosineSimilarity(lang, title1, title2):
    # Prepare the URL.
    data = urllib.parse.urlencode([("lang", lang),
        ("title1", title1), ("title2", title2)])
    url = "http://www.wikifier.org/get-cosine-similarity?" + data
    # Call the Wikifier and read the response.
    with urllib.request.urlopen(url, timeout = 60) as f:
        response = f.read()
        response = json.loads(response.decode("utf8"))
    # Return the cosine similarity between the TF-IDF vectors.
    return response["cosTfIdfVec"]

#print(CosineSimilarity("en", "New York", "New York City"))

#def dbpediashortpath(start_label, end_label):
#    query ="""
#    PREFIX dbo: <http://dbpedia.org/ontology/>
#    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

#    SELECT ?path
#    WHERE {
#      ?start dbo:wikiPageLabel "%s" ;
#        dbo:wikiPageRedirects ?end .
#      ?end dbo:wikiPageLabel "%s" .
#      ?path rdf:first ?start ;
#        rdf:rest* ?rest .
#      FILTER (?end = ?endLabel)
#    }
#    ORDER BY ?path
#"""
   
#    escaped_query = re.sub(r"\n", r"\\n", query)

#    # Execute the SPARQL query
#    results = sparql.query(query, (start_label, end_label))

#    # Print the shortest path
#    path = results["results"]["bindings"][0]["path"]["value"]
#    print(path)
#    return path

#def DBpedia_short_path(start_entity, end_entity):
#    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
#    sparql.setQuery(   f"""
#     PREFIX dbo: <http://dbpedia.org/ontology/>
#     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#     PREFIX dbr: <http://dbpedia.org/resource/>
#     SELECT ?path
#     WHERE {{
#      ?start dbo:wikiPageLabel dbr:{start_entity} ;
#        dbo:wikiPageRedirects ?end .
#      ?end dbo:wikiPageLabel dbr:{end_entity} .
#      ?path rdf:first ?start ;
#       rdf:rest* ?rest .
#      FILTER (?end = ?endLabel)
#        }}
#         ORDER BY ?path
#    """)
    
#    sparql.setReturnFormat(JSON)
    
#    results = sparql.query().convert()
#    # Execute the SPARQL query
#    #results = sparql.queryAndConvert(JSON)

#    # Print the shortest path
#    #path = results["results"]["bindings"][0]["path"]["value"]
#    print(results)
#    return results

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
