import rdflib
from rdflib.namespace import XSD
 
prefixes = {
    "ex": "http://example.com/",
    "xsd": XSD.NS
}

#questa funzione trasforma un set di triple in un grafo di conoscenza con prefissi prestability
def transform_triples(triples, prefixes):
    g = Graph()
    for subject, predicate, object in triples:
        subject_with_prefix = "{}{}".format(prefixes["ex"], subject)
        predicate_with_prefix = "{}{}".format(prefixes["ex"], predicate)
        object_with_prefix = "{}{}".format(prefixes["ex"], object)

        g.add((rdflib.URIRef(subject_with_prefix), rdflib.URIRef(predicate_with_prefix), rdflib.URIRef(object_with_prefix)))
        print(g)
    return g

# Example usage
#triples = [("subject1", "predicate1", "object1"), ("subject2", "predicate2", "object2")]
#transformed_graph = transform_triples(triples)

## Print the transformed RDF triples
#print(transformed_graph)
