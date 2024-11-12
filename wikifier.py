import requests

import urllib.parse, urllib.request, json

def CallWikifier(text, lang="en", threshold=0.6):
   
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
    # for annotation in response["annotations"]:
    #     if title == "":
    #          title  = annotation["title"]
    #     try:
    #         annotazione = (annotation["secTitle"], ",".join(annotation["dbPediaTypes"]), annotation["secUrl"])
    #     except Exception as e:
    #         annotazione = (annotation["title"], ",".join(annotation["dbPediaTypes"]), annotation["url"])
           
    #     annotazioni.append(annotazione)

    #     with open(f"entitiesfromwikificationeng{title}.txt", "a") as f:
    #         try:
    #             f.write(str(annotation["secTitle"]) + ",")
    #         except Exception as e:
    #             f.write(str(annotation["title"]) + ",")
    #     with open(f"entitiesfromwikification{lang}{title}.txt", "a") as l:
    #         try:
    #             l.write(str(annotation["title"]) + ",")
    #         except Exception as e:
    #             pass
    #     with open(f"urlsfromwikificationeng{title}.txt", "a") as g:
    #         try:
    #             g.write(str(annotation["secUrl"]) + ",")
    #         except Exception as e:
    #             g.write(str(annotation["url"]) + ",")
    #     with open(f"urlsfromwikification{title}.txt", "a") as m:
    #         try:
    #             m.write(str(annotation["url"]) + ",")
    #         except Exception as e:
    #             g.write(str(annotation["url"]) + ",")
    # f.close()
    # g.close()
    # l.close()
    # m.close()

    # print(str(annotazioni))
    
    # with open(f"triplesfromwikification{title}.txt", "a") as f:
    #     f.write(str(annotazioni))
    #     f.close()
    annotations = []  
    if "annotations" in response:
        for annotation in response["annotations"]:
            types = []
            if "wikiDataClasses" in annotation:
                types = [cls["enLabel"] for cls in annotation["wikiDataClasses"]]
                
            annotation_data = {
                "uri": annotation["url"],
                "surface_form": annotation["title"],
                #"offset": annotation["characters"][0]["chFrom"],
                "types": types
            }
            annotations.append(annotation_data)
        
    return annotations #annotazioni?


#text = "The year 1942 was a tumultuous time globally"
#CallWikifier(text)