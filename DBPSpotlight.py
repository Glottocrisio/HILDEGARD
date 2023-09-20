import requests


def entitylinking(text):
    url ="https://api.dbpedia-spotlight.org/it/annotate"
    headers={'accept':'application/json'}

    resp = requests.get(url, headers=headers, params={"text": text})
     
    data = resp.json()
    print(data)
    return data

#if response.status_code == 200:
#    data = response.json()
#    resources = data["Resources"]
#    for resource in resources:
#        print("Surface Form:", resource["@surfaceForm"])
#        print("URI:", resource["@URI"])
#        print("Types:", resource["@types"])
#        print()
#else:
#    print("Error:", response.status_code)