import requests
from neo4j import GraphDatabase
from SPARQLWrapper import SPARQLWrapper, JSON, RDF, TURTLE
#import beautifulsoup4 as bs


def fetchSPARQLendpoint(text, endpoint, lang, obj_list):
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
        
    elif endpoint == "a":
        sparql = SPARQLWrapper("https://dati.cultura.gov.it/sparql")
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

            # Execute the query
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
            FILTER(LANG(?title) = '"""+ lang +"""')    }
        """
            sparql.setQuery(query)
            sparql.setReturnFormat(TURTLE)
            results = sparql.query().convert()
            
        

            #    # Specify the folder and file path to save the results
            #    file_path = "C:/Users/Palma/Desktop/PHD/DatasetThesis/HildegardData/"
            #    file_path = filepath + input("Insert the name of the file you want to save as KB:")
            #    # Save the results to the specified file
            #    with open(file_path, 'w') as file:
            #        file.write(result_data)  
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
            sparql.setReturnFormat(TURTLE)
            results = sparql.query().convert()

 
            # Specify the folder and file path to save the results
            file_path = "C:\\Users\\Palma\\Desktop\\PHD\\DatasetThesis\\HildegardData\\"
            file_path = file_path + input("Insert the name of the file you want to save as KB:")
            # Save the results to the specified file
            with open(file_path, 'w') as file:
                file.write(str(results))

     
