import requests
from neo4j import GraphDatabase
from SPARQLWrapper import SPARQLWrapper, JSON, RDF, TURTLE
from rdflib import Graph, Namespace, URIRef
import ssl
import urllib.request



def fetchSPARQLendpoint(endpoint, lang, obj_list=None):
    if endpoint == "w":
        sparql = SPARQLWrapper(
            "https://query.wikidata.org/sparql/"
        )
        
    elif endpoint == "y":
        sparql = SPARQLWrapper(
            "https://yago-knowledge.org/sparql/"
        )
       
    elif endpoint == "d":
        sparql = SPARQLWrapper(
            "https://dbpedia.org/sparql/"
        )
        
    elif endpoint == "e":
        sparql = SPARQLWrapper(
            "https://sparql.europeana.eu/"
        )
        query = """
            PREFIX edm: <http://www.europeana.eu/schemas/edm/>


            SELECT DISTINCT ?Dataset
            WHERE {
              ?Aggregation edm:collectionName ?Dataset;
 	            edm:language ?language.

              VALUES ?language {\"""" + str(lang) + """\"}
            }


        """
        
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        ssl._create_default_https_context = ssl._create_unverified_context
        # # Create an unverified SSL context
        # context = ssl._create_unverified_context()

        # # Use this context to open a URL
        # response = urllib.request.urlopen('https://sparql.europeana.eu/', context=context)
        #print(response.read())
        results = sparql.query().convert()
        i = 0
        while i <  len(results['results']['bindings']):
            print(results['results']['bindings'][i]['Dataset']['value'])
            i = i + 1
            
        datapro = input("Insert the name of the dataset you want to explore, from the previous output:\n")
        query =  """
            PREFIX edm: <http://www.europeana.eu/schemas/edm/>
            PREFIX dc: <http://purl.org/dc/elements/1.1/>
            PREFIX dcterms: <http://purl.org/dc/terms/>

            SELECT DISTINCT ?museo ?cultobj ?title ?descr
            WHERE {
              ?aggregation edm:collectionName \"""" + str(datapro) + """\";
                           edm:aggregatedCHO ?cultobj.
              ?Proxy ore:proxyFor ?cultobj;
  	            dc:title ?title;
                    dc:description ?descr.
              BIND(\"""" + str(datapro) + """\" AS ?museo)
        """
        if obj_list != None:
            i = 0
            while i < len(obj_list):
                query = query + f"""CONTAINS(?title, "{obj_list[i]}") || CONTAINS(?descr, "{obj_list[i]}")"""
                if i + 1 != len(obj_list):
                    query = query + """ || """
                i = i + 1
            query = query + """)
            }"""
        else:
            query = query + """  }"""
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)

        results = sparql.query().convert()
        i = 0
        while i <  len(results['results']['bindings']):
            print(results['results']['bindings'][i]['object']['value'])
            i = i + 1

    elif endpoint == "a":
        sparql = SPARQLWrapper("https://dati.cultura.gov.it/sparql")
        while True:
            try:
                text =     input("Da dove vuoi partire nella tua ricerca di oggetti culturali?"
                + "Digita 'region' o 'museum': \n" + "Where do you want to start your search for heritage objects?"
                + "Type 'region' or 'museum': \n")
                if text == "region" or text == "museum":
                    # Valid input
                    break
                else:
                    print("Invalid input. Please type 'region' or 'museum'.\n"
                            +"Input non valido. Prego inserire 'region' oppure 'museum': \n")
            except Exception as e:
                print(f"An error occurred: {e}")
        if text=="region":
            region = input("Insert the name of the region you want to explore: \n")
            query = """
                PREFIX arco-arco: <https://w3id.org/arco/ontology/arco/>
                PREFIX arco-location: <https://w3id.org/arco/ontology/location/>
                PREFIX CLV: <https://w3id.org/italia/onto/CLV/>
                PREFIX arco-dd: <https://w3id.org/arco/ontology/denotative-description/>
                SELECT  distinct ?cultpro ?id ?type ?title ?description ?address ?regNome ?def
                WHERE {
                ?cultpro a arco-arco:ArchitecturalOrLandscapeHeritage.
                ?cultpro dc:identifier ?id.
                ?cultpro dc:title ?title.
                ?cultpro dc:description ?description.
                ?cultpro arco-location:hasCulturalPropertyAddress ?address.
                ?address CLV:hasRegion ?region.
                ?region rdfs:label ?regNome.
                ?cultpro arco-dd:hasCulturalPropertyType ?type.
                ?type arco-dd:hasCulturalPropertyDefinition ?def.
                FILTER regex(?regNome, \"""" + str(region) + """\", \"i")
                FILTER regex(?def, \"museo\", \"i")     } 
            """
               
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)

            results = sparql.query().convert()
            i = 0
            while i <  len(results['results']['bindings']):
                print(results['results']['bindings'][i]['title'])
                i = i + 1
            
            museo = input("Insert the name of the museum or site you want to explore, from the previous output:\n")
            query =  """
                    PREFIX cov: <https://w3id.org/italia/onto/COV/>
                    PREFIX arco-core: <https://w3id.org/arco/ontology/core/>
                    PREFIX datigov: <http://dati.gov.it/onto/>
                    PREFIX dcterms: <http://purl.org/dc/terms/>
                    PREFIX io: <https://schema.gov.it/lodview/onto/l0/>
                    PREFIX cis: <http://dati.beniculturali.it/cis/>

                    SELECT DISTINCT ?cultpro
                    WHERE {{
                        ?cultpro rdfs:label \"""" + str(museo) + """\".
                        ?cultpro rdf:type cov:Organization
                    }
                    UNION
                    {
                        ?cultpro rdfs:label \"""" + str(museo) + """\".
                        ?cultpro rdf:type cis:CulturalInstituteOrSite
                    }}
                    LIMIT 2
                """
            
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            i = 0
            while i <  len(results['results']['bindings']):
                if i == 0:
                    catalogagencydict = results['results']['bindings'][i]
                    catalogagency = catalogagencydict['cultpro']['value']
                else:
                    cultinstdict = results['results']['bindings'][i]
                    cultinst = cultinstdict['cultpro']['value']
                print(results['results']['bindings'][i])
                i = i + 1

            query = """
            PREFIX arco-arco: <https://w3id.org/arco/ontology/arco/>
            PREFIX arco-arco: <https://w3id.org/arco/ontology/arco/>
            PREFIX arco-location: <https://w3id.org/arco/ontology/location/>
            PREFIX CLV: <https://w3id.org/italia/onto/CLV/>
            PREFIX arco-dd: <https://w3id.org/arco/ontology/denotative-description/>
            PREFIX cov: <https://w3id.org/italia/onto/COV/>
            PREFIX arco-core: <https://w3id.org/arco/ontology/core/>
            PREFIX datigov: <http://dati.gov.it/onto/>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX io:  <https://w3id.org/italia/onto/l0/>
            
            SELECT DISTINCT ?cultobj ?title ?museo ?descr
            WHERE {
            {?cultobj arco-arco:hasCataloguingAgency  <""" + str(catalogagency) + """>.
                    <""" + str(catalogagency) + """>  rdfs:label  ?museo.
                ?cultobj   dc:description ?descr.
                ?cultobj  rdfs:label ?title}
                union
                {?cultobj  arco-location:hasCulturalInstituteOrSite <""" + str(cultinst) + """>.
                <""" + str(cultinst) + """> rdfs:label  ?museo.
                ?cultobj   dc:description ?descr.
                ?cultobj  rdfs:label ?title }
            FILTER(LANG(?title) = '"""+ lang +"""')    }"""
            if len(obj_list) == 0:
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            
            else:            
                i = 0
                query = query[:-1] + """FILTER ("""
                while i < len(obj_list):
                    query = query + f"""CONTAINS(?title, "{obj_list[i]}") || CONTAINS(?descr, "{obj_list[i]}")""" 
                    if i + 1 != len(obj_list):
                        query = query + """ || """
                    i = i + 1
                query = query + """)
                }"""
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
        
        else:
            museo = input("Insert the name of the museum or site you want to explore:\n")
            query =  """
                    PREFIX cov: <https://w3id.org/italia/onto/COV/>
                    PREFIX arco-core: <https://w3id.org/arco/ontology/core/>
                    PREFIX datigov: <http://dati.gov.it/onto/>
                    PREFIX dcterms: <http://purl.org/dc/terms/>
                    PREFIX io: <https://schema.gov.it/lodview/onto/l0/>
                    PREFIX cis: <http://dati.beniculturali.it/cis/>

                    SELECT DISTINCT ?cultpro
                    WHERE {{
                        ?cultpro rdfs:label \"""" + str(museo) + """\".
                        ?cultpro rdf:type cov:Organization
                    }
                    UNION
                    {
                        ?cultpro rdfs:label \"""" + str(museo) + """\".
                        ?cultpro rdf:type cis:CulturalInstituteOrSite
                    }}
                    LIMIT 2
                """
            
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            i = 0
            while i <  len(results['results']['bindings']):
                if i == 0:
                    catalogagencydict = results['results']['bindings'][i]
                    catalogagency = catalogagencydict['cultpro']['value']
                else:
                    cultinstdict = results['results']['bindings'][i]
                    cultinst = cultinstdict['cultpro']['value']
                print(results['results']['bindings'][i])
                i = i + 1

            query = """
            PREFIX arco-arco: <https://w3id.org/arco/ontology/arco/>
            PREFIX arco-arco: <https://w3id.org/arco/ontology/arco/>
            PREFIX arco-location: <https://w3id.org/arco/ontology/location/>
            PREFIX CLV: <https://w3id.org/italia/onto/CLV/>
            PREFIX arco-dd: <https://w3id.org/arco/ontology/denotative-description/>
            PREFIX cov: <https://w3id.org/italia/onto/COV/>
            PREFIX arco-core: <https://w3id.org/arco/ontology/core/>
            PREFIX datigov: <http://dati.gov.it/onto/>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX io:  <https://w3id.org/italia/onto/l0/>
            
            SELECT DISTINCT ?cultobj ?title ?museo ?descr
            WHERE {
            {?cultobj arco-arco:hasCataloguingAgency  <""" + str(catalogagency) + """>.
                    <""" + str(catalogagency) + """>  rdfs:label  ?museo.
                ?cultobj   dc:description ?descr.
                ?cultobj  rdfs:label ?title}
                union
                {?cultobj  arco-location:hasCulturalInstituteOrSite <""" + str(cultinst) + """>.
                <""" + str(cultinst) + """> rdfs:label  ?museo.
                ?cultobj   dc:description ?descr.
                ?cultobj  rdfs:label ?title }
            FILTER(LANG(?title) = '"""+ lang +"""')   
            FILTER("""

            i = 0
            while i < len(obj_list):
                query = query + f"""CONTAINS(?title, "{obj_list[i]}") || CONTAINS(?descr, "{obj_list[i]}")"""
                if i + 1 != len(obj_list):
                    query = query + """ || """
                i = i + 1
            query = query + """)
            }"""
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

    g = Graph()

    #for result in results["results"]["bindings"]:
    #    subject = result["subject"]["value"]
    #    predicate = result["predicate"]["value"]
    #    obj = result["object"]["value"]

    #    g.add((URIRef(subject), URIRef(predicate), URIRef(obj)))

    #turtle_data = g.serialize(format='turtle')

    #print(turtle_data.decode()) 

    file_path = "C:\\Users\\Palma\\Desktop\\PHD\\***\\HildegardData\\"
    file_path = file_path + input("Insert the name of the file you want to save as KB:")
    # Save the results to the specified file
    global file_path_json_kb
    file_path_json_kb = file_path
    with open(file_path, 'w') as file:
        file.write(str(results))



#fetchSPARQLendpoint('region', 'e', 'it')