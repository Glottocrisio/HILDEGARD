import requests

import urllib.parse, urllib.request, json

def CallWikifier(text, lang="it", threshold=0.9):
   
    data = urllib.parse.urlencode([
        ("text", text), ("lang", lang),
        ("userKey", "mjxwdfdvrjmgkrlimhzkoumetmkacy"),
        ("pageRankSqThreshold", "%g" % threshold), ("applyPageRankSqThreshold", "true"),
        ("nTopDfValuesToIgnore", "200"), ("nWordsToIgnoreFromList", "200"),
        ("wikiDataClasses", "true"), ("wikiDataClassIds", "false"),
        ("support", "true"), ("ranges", "false"), ("minLinkFrequency", "2"),
        ("includeCosines", "false"), ("maxMentionEntropy", "3")
        ])
    url = "http://www.wikifier.org/annotate-article"
   
    req = urllib.request.Request(url, data=data.encode("utf8"), method="POST")
    with urllib.request.urlopen(req, timeout = 60) as f:
        response = f.read()
        response = json.loads(response.decode("utf8"))
   
    annotazioni = []
    title = ""
    #with open(f"entitiesfromwikification.txt", "w") as file:
    #    file.write("")
    #    f.close()
    for annotation in response["annotations"]:
        if title == "":
             title  = annotation["title"]
        try:
            annotazione = (annotation["secTitle"], ",".join(annotation["dbPediaTypes"]), annotation["secUrl"])
        except Exception as e:
            annotazione = (annotation["title"], ",".join(annotation["dbPediaTypes"]), annotation["url"])
           
        annotazioni.append(annotazione)

        with open(f"entitiesfromwikification{title}.txt", "a") as f:
            try:
                f.write(str(annotation["secTitle"]) + ",")
            except Exception as e:
                f.write(str(annotation["title"]) + ",")
        with open(f"urlsfromwikification{title}.txt", "a") as g:
            try:
                g.write(str(annotation["secUrl"]) + ",")
            except Exception as e:
                g.write(str(annotation["url"]) + ",")
        f.close()
        g.close()
    print(str(annotazioni))
    
    with open(f"triplesfromwikification{title}.txt", "a") as f:
        f.write(str(annotazioni))
        f.close()

    return annotazioni