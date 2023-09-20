import requests
from neo4j import GraphDatabase
from SPARQLWrapper import SPARQLWrapper, JSON, RDF, TURTLE
#import beautifulsoup4 as bs



def fetchSPARQLendpoint(text, endpoint, lang):
    if endpoint == "wikidata":
        sparql = SPARQLWrapper(
            "https://query.wikidata.org/sparql/"
        )
        sparql.setReturnFormat(JSON)
    elif endpoint == "yago":
        sparql = SPARQLWrapper(
            "https://yago-knowledge.org/sparql/"
        )
        sparql.setReturnFormat(JSON)
    elif endpoint == "dbpedia":
        sparql = SPARQLWrapper(
            "https://dbpedia.org/sparql/"
        )
        sparql.setReturnFormat(JSON)
    elif endpoint == "europeana":
        sparql = SPARQLWrapper(
            "https://sparql.europeana.eu/"
        )
        sparql.setReturnFormat(JSON)
    elif endpoint == "arco":
        sparql = SPARQLWrapper(
            "https://dati.cultura.gov.it/sparql/"
        )
        sparql.setReturnFormat(JSON)
        if text="region":
            region = input("Insert the name of the region you want to explore:")
            sparql.setQuery( "PREFIX arco-arco: <https://w3id.org/arco/ontology/arco/>\n"
            "PREFIX arco-location: <https://w3id.org/arco/ontology/location/>\n"
            "PREFIX CLV: <https://w3id.org/italia/onto/CLV/>\n"
            "PREFIX arco-dd: <https://w3id.org/arco/ontology/denotative-description/>\n"
            "SELECT  distinct ?cultpro ?id ?type ?title ?description ?address ?regNome ?def\n"
            "WHERE {\n"
             "?cultpro a arco-arco:ArchitecturalOrLandscapeHeritage.\n"
             "?cultpro dc:identifier ?id.\n"
             "?cultpro dc:title ?title.\n"
             "?cultpro dc:description ?description.\n"
             "?cultpro arco-location:hasCulturalPropertyAddress ?address.\n"
             "?address CLV:hasRegion ?region.\n"
             "?region rdfs:label ?regNome.\n"
             "?cultpro arco-dd:hasCulturalPropertyType ?type.\n"
             "?type arco-dd:hasCulturalPropertyDefinition ?def\n"
             "FILTER regex(?regNome, " + str(region) + 
             ", \"i"")\n"
             "FILTER regex(?def, \"museo", "i"")\n       } "
         
             )

        if text=="museum":
            museo = input("Insert the name of the museum you want to explore:")
            sparql.setQuery( 
                "PREFIX CLV: <https://w3id.org/italia/onto/CLV/>\n"
                "PREFIX arco-dd: <https://w3id.org/arco/ontology/denotative-description/>\n"
                "PREFIX cov: <https://w3id.org/italia/onto/COV/>\n"
                "PREFIX arco-core: <https://w3id.org/arco/ontology/core/>\n"
                "PREFIX datigov: <http://dati.gov.it/onto/>\n"
                "PREFIX dcterms: <http://purl.org/dc/terms/>\n"
                "PREFIX io:  <https://w3id.org/italia/onto/l0/>\n\n"

                "SELECT DISTINCT ?cultpro\n"
                "WHERE {\n"
                " {?cultpro a cov:Organization.\n"
                " ?cultpro  rdfs:label" + str(museo)+  "}\n"
                " UNION\n"
                " {?cultpro owl:sameAs <http://dati.beniculturali.it/mibact/luoghi/resource/CulturalInstituteOrSite/20333>}\n"
                "}\n"
                  )

            try:
                ret = sparql.queryAndConvert()

                # works for "p" values extracted from wikidata
                uri = ret["results"]["bindings"][0]["p"]["value"]

                info = {
                    "uri" : uri,
                    "label" : text
                }

                return info

            except Exception as e:
                print(e)

                return 0

            sparql.setQuery("PREFIX arco-arco: <https://w3id.org/arco/ontology/arco/>\n"
            "PREFIX arco-arco: <https://w3id.org/arco/ontology/arco/>\n"
            "PREFIX arco-location: <https://w3id.org/arco/ontology/location/>\n"
            "PREFIX CLV: <https://w3id.org/italia/onto/CLV/>\n"
            "PREFIX arco-dd: <https://w3id.org/arco/ontology/denotative-description/>\n"
            "PREFIX cov: <https://w3id.org/italia/onto/COV/>\n"
            "PREFIX arco-core: <https://w3id.org/arco/ontology/core/>\n"
            "PREFIX datigov: <http://dati.gov.it/onto/>\n"
            "PREFIX dcterms: <http://purl.org/dc/terms/>\n"
            "PREFIX io:  <https://w3id.org/italia/onto/l0/>\n"
            "PREFIX a-res: <>\n\n"
            "SELECT DISTINCT ?cultobj ?title ?museo ?descr\n"
            "WHERE {\n\n"
            "{?cultobj arco-arco:hasCataloguingAgency " + str(catalogagency) +  ".\n"
                + str(catalogagency) +  "rdfs:label  ?museo.\n"
            "    ?cultobj   dc:description ?descr.\n"
            "    ?cultobj  rdfs:label ?title}\n"
            "  union\n"
            "  {?cultobj  arco-location:hasCulturalInstituteOrSite " + str(cultinst) + ".\n"
             + str(cultinst) + " rdfs:label  ?museo.\n"
            "   ?cultobj   dc:description ?descr.\n"
            "   ?cultobj  rdfs:label ?title\n}\n"
            "FILTER(LANG(?title) = 'it')\n""     }"
        )

            try:
                ret = sparql.queryAndConvert()

                # works for "p" values extracted from wikidata
                uri = ret["results"]["bindings"][0]["p"]["value"]

                info = {
                    "uri" : uri,
                    "label" : text
                }

                return info

            except Exception as e:
                print(e)

                return 0
     

## Simple test of SPARQL Query
#text = "Campania"
#lang = "it"
#endpoint = "arco"
#prop = SparqlQuery(text)
#print(prop)
     
      #{?cultobj arco-arco:hasCataloguingAgency <https://w3id.org/arco/resource/Agent/0ba919527878dcea78885b142e4682b0>.
	     #       <https://w3id.org/arco/resource/Agent/0ba919527878dcea78885b142e4682b0>  rdfs:label  ?museo.
	     #       ?cultobj   dc:description ?descr.
	     #       ?cultobj  rdfs:label ?title}
      #        union
      #        {?cultobj  arco-location:hasCulturalInstituteOrSite <https://w3id.org/arco/resource/CulturalInstituteOrSite/8d130d98a822a8850d90265edb9df57a>.
      #         <https://w3id.org/arco/resource/CulturalInstituteOrSite/8d130d98a822a8850d90265edb9df57a> 