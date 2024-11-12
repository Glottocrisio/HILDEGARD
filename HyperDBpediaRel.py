from SPARQLWrapper import SPARQLWrapper, JSON
import re


def execute_query(query):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

def generate_query(num_mids, entity1, entity2):
    query = f"""PREFIX dbo: <http://dbpedia.org/ontology/> 
PREFIX dbr: <http://dbpedia.org/resource/> 
PREFIX owl: <http://www.w3.org/2002/07/owl#> 
SELECT ?entity1 {" ".join([f"?pf{i} ?mid{i}" for i in range(1, num_mids + 1)])} ?pf{num_mids + 1} ?entity2 
WHERE {{ 
VALUES (?entity1 ?entity2) {{ (dbr:{entity1} dbr:{entity2})}} 
?entity1 ?pf1 ?mid1. 
"""
    
    for i in range(1, num_mids + 1):
        query += f"""?mid{i} ?pf{i+1} ?mid{i+1}. \n"""
    
    query += f"""?mid{num_mids+1} ?pf{num_mids+2} ?entity2\n"""
    
    query += """FILTER(?entity1 != ?mid1 && ?entity2 != ?mid1 """
    for i in range(1, num_mids+2):
        if i == 5:
             pass
        else:
           query += f"&& ?mid{i} != ?mid{i+1} "
    query += """) \n"""
    
    for i in range(1, num_mids + 3):
        if i == 5:
             pass
        else:
             query += f"""FILTER (?pf{i} NOT IN (dbo:Person, dbo:wikiPageWikiLink, owl:Thing)) \n"""
    
    query += """} LIMIT 20"""
    return query

def process_entity_pair(entity1, entity2):
    print(f"\nProcessing pair: {entity1} - {entity2}")
    num_mids = 1
    while True:
        query = generate_query(num_mids, entity1, entity2)
        print(f"Executing query with {num_mids} mid(s)...")
        results = execute_query(query)
        
        if results:
            print("Results found:")
            for result in results:
                print(result)
            break
        else:
            print("No results found. Increasing the number of mids.")
            num_mids += 1
        
        if num_mids > 7:  # Arbitrary limit to prevent infinite loop
            print("Reached maximum number of mids without results.")
            break


def extract_entity_pairs(content):
    pairs = re.findall(r"'([^']+)'; '([^']+)'", content)
    return list(set(pairs))  

def extract_entities(text):
    # Split the text by '>>' to separate each entity
    entries = text.split('>>')
    
    # Use a set comprehension to extract unique entities
    # The regular expression removes numbers, 'W', 'D', and spaces at the start of each entry
    entities = {re.sub(r'^[\d.\s]+[WD]\s*', '', entry.strip()) for entry in entries if entry.strip()}
    
    return entities


text = """0.0269World War II W DWorld War II>>0.0198Luxembourg W DLuxembourg>>0.0133Nazi Germany W DNazi Germany>>0.0065Resistance movement DResistance movement>>0.0054Social norm DSocial norm>>0.0053Wehrmacht W DWehrmacht>>0.0050Technology W DTechnology>>0.0049Symbol DSymbol>>0.0046Anschluss W DAnschluss>>0.0045Society W DSociety>>0.0045Globalization W DGlobalization>>0.0045Bicycle W DBicycle>>0.0043Freedom of the press DFreedom of the press>>0.0042Honeymoon DHoneymoon>>0.0041Historiography W DHistoriography>>0.0041Forced labour DForced labour>>"""

result = extract_entities(text)
print(result)

def main():
    content_random = '''
'Barney_(given_name)'; 'Barney_Stinson'; '12'
'Wayne_Brady'; 'Barney_Stinson'; '19'
'Armenian_Apostolic_Church'; 'Cyril_of_Alexandria'; '29'
'List_of_Copts'; 'Cyril_of_Alexandria'; '10'
'Ralph_Macchio'; 'Barney_Stinson'; '18'
'Nestorius'; 'Cyril_of_Alexandria'; '226'
'Mendoza_Line'; 'Barney_Stinson'; '13'
'Pelagius'; 'Cyril_of_Alexandria'; '36'
'Frances_Conroy'; 'Barney_Stinson'; '19'
'Witch-hunt'; 'Cyril_of_Alexandria'; '30'
'Dyophysitism'; 'Cyril_of_Alexandria'; '27'
'Tomb_of_Alexander_the_Great'; 'Cyril_of_Alexandria'; '23'
'Becki_Newton'; 'Barney_Stinson'; '10'
'History_of_the_Jews_in_Egypt'; 'Cyril_of_Alexandria'; '25'
'John_Chrysostom'; 'Cyril_of_Alexandria'; '16'
'Main_Page'; 'Barney_Stinson'; '28'
'List_of_venerated_persons_from_Africa'; 'Cyril_of_Alexandria'; '19'
'List_of_breakout_characters'; 'Barney_Stinson'; '33'
'Robin_Scherbatsky'; 'Barney_Stinson'; '659'
'Church_Fathers'; 'Cyril_of_Alexandria'; '64'
'April_Bowlby'; 'Barney_Stinson'; '39'
'Miaphysitism'; 'Cyril_of_Alexandria'; '82'
'Neil_Patrick_Harris'; 'Barney_Stinson'; '542'
'Ethiopian_Orthodox_Tewahedo_Church'; 'Cyril_of_Alexandria'; '87'
'Ted_Mosby'; 'Barney_Stinson'; '74'
'Library_of_Alexandria'; 'Cyril_of_Alexandria'; '18'
'List_of_patriarchs_of_Alexandria'; 'Cyril_of_Alexandria'; '14'
'How_I_Met_Your_Father'; 'Barney_Stinson'; '261'
'Oriental_Orthodox_Churches'; 'Cyril_of_Alexandria'; '20'
'Last_Forever'; 'Barney_Stinson'; '11'
'Pope_Leo_I'; 'Cyril_of_Alexandria'; '23'
'Lily_Aldrin'; 'Barney_Stinson'; '86'
'Marshall_Eriksen'; 'Barney_Stinson'; '258'
'Hypatia_(novel)'; 'Cyril_of_Alexandria'; '12'
'List_of_islands_by_area'; 'Bolshevik_Island'; '96'
'Patristics'; 'Cyril_of_Alexandria'; '22'
'First_seven_ecumenical_councils'; 'Cyril_of_Alexandria'; '10'
'List_of_islands_of_Russia'; 'Bolshevik_Island'; '36'
'Desert_island'; 'Bolshevik_Island'; '52'
'Theophilus_I_of_Alexandria'; 'Cyril_of_Alexandria'; '106'
'Alexandrian_liturgical_rites'; 'Cyril_of_Alexandria'; '15'
'Athanasius_of_Alexandria'; 'Cyril_of_Alexandria'; '39'
'Severnaya_Zemlya'; 'Bolshevik_Island'; '43'
'List_of_Coptic_Orthodox_popes'; 'Cyril_of_Alexandria'; '28'
'Second_Council_of_Ephesus'; 'Cyril_of_Alexandria'; '18'
'Second_Council_of_Constantinople'; 'Cyril_of_Alexandria'; '12'
'Sextus_Julius_Severus'; 'Troubleshooting'; '16'
'Voltaire'; 'Cyril_of_Alexandria'; '10'
    '''


    entity_couples = '''
    'Honey_Moon '; 'Belle_\u00C9poque'
    '''

    entity_pairs = extract_entity_pairs(entity_couples)
    
    for entity1, entity2 in entity_pairs:
        process_entity_pair(entity1, entity2)

if __name__ == "__main__":
    main()
