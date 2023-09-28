import requests

from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON


# Function to query Wikidata based on a DBpedia URI
def query_wikidata(dbpedia_uri):
    wikidata_api_url = "https://www.wikidata.org/w/api.php"
    
    # Define parameters for the Wikidata API query
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": dbpedia_uri,
    }
    
    # Send the API request
    response = requests.get(wikidata_api_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "search" in data and data["search"]:
            # Extract Wikidata entity information
            wikidata_id = data["search"][0]["id"]
            label = data["search"][0]["label"]
            description = data["search"][0]["description"]
            
            return {
                "Wikidata ID": wikidata_id,
                "Label": label,
                "Description": description,
            }
    else:
        print("Error:", response.status_code)
    
    return None


# Function to query YAGO for matching entities

def query_yago(dbpedia_uri):
    # YAGO SPARQL endpoint
    sparql_endpoint = "https://yago-knowledge.org/sparql/query"

    # Define your SPARQL query to search for YAGO entities based on DBpedia URI
    sparql_query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX yago: <http://yago-knowledge.org/resource/>
        SELECT ?yagoEntity
        WHERE {{
            ?yagoEntity owl:sameAs <{dbpedia_uri}> .
        }}
    """

    # Set up the SPARQL wrapper
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)

    # Execute the query
    results = sparql.query().convert()

    if "results" in results and "bindings" in results["results"]:
        # Extract YAGO entity URIs from the results
        yago_entities = [binding["yagoEntity"]["value"] for binding in results["results"]["bindings"]]
        return yago_entities

    return None

def queryBabelnet(dbpedia_uri):
    babelnet_api_url = "https://babelnet.io/v6/getSynsetIds"

    # Specify your BabelNet API key here
    api_key = "3b5675dd-da75-4c2c-b727-c3edf92e4635"

    # Define the query parameters
    query = dbpedia_url.replace("http://it.dbpedia.org/resource/", "")  # Replace with your desired word

    # Set up the request headers with your API key
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # Define the query parameters
    params = {
        "word": query,
    }

    try:
        # Send the GET request
        response = requests.get(babelnet_api_url, headers=headers, params=params)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Extract information from the response as needed
            print("Synset IDs:", data)
            return data
        else:
            print("Error:", response.status_code, response.text)

    except Exception as e:
        print("An error occurred:", str(e))


def queryEuropeana(dbpedia_uri):
    europeana_api_url = "https://www.europeana.eu/api/v2/search.json"

    # Define your API key (if required)
    api_key = "armedinguil"  # Replace with your actual API key if needed

    # Define the search query
    query = dbpedia_url.replace("http://it.dbpedia.org/resource/", "")  # Replace with your desired query

    # Set up the request parameters
    params = {
        "query": query,
        # You can add more parameters here as needed, such as "rows" for the number of results
    }

    # If you need to include your API key in the request headers, uncomment the following lines:
    # headers = {
    #     "Api-Key": api_key,
    # }

    try:
        # Send the GET request
        response = requests.get(europeana_api_url, params=params, headers=headers if "api_key" in locals() else None)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
        
            # Extract and process the relevant information from the response
            for item in data.get("items", []):
                # Access item metadata as needed
                title = item.get("title", "")
                # Print or process other metadata fields as needed
                print("Title:", title)
                return title
        else:
            print("Error:", response.status_code, response.text)

    except Exception as e:
        print("An error occurred:", str(e))