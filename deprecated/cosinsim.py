import urllib.parse, urllib.request, json

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

print(CosineSimilarity("en", "New York", "New York City"))
