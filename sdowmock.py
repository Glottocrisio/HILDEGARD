import requests
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support import expected_conditions as EC
import os

def related_entities(start, end):
    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    browser = webdriver.Firefox(executable_path=r'C:\Program Files\Mozilla Firefox\gecko\geckodriver.exe', options=options)
    #?source=Alexander the Great&target=Bible
    browser.get((f"https://www.sixdegreesofwikipedia.com/?source={start}&target={end}"))
    #browser.find_element_by_id("start_node").send_keys("Albert_Einstein")
    #browser.find_element_by_id("end_node").send_keys("Barack_Obama")
    #find_element(By.CSS_SELECTOR, "svg").

    browser.find_element(By.CSS_SELECTOR, "button").click()
    browser.find_element(By.CSS_SELECTOR, "div")
    browser.find_element(By.CSS_SELECTOR, "svg")

    #browser.find_element(By.CSS_SELECTOR, "g")
    browser.find_elements(By.CLASS_NAME, "node-labels")
    nodelist = browser.find_elements(By.CSS_SELECTOR, "text")

    nodes = []
    for node in nodelist:
        #node.get_attribute("innerHTML")
        nodes.append(node.text)
   
    print(nodes)
    browser.close()

    return nodes


def delete_until_word(string, word, n):

  count = string.count(word)
  if count < n:
    return string

  index = -1
  for i in range(count):
    index = string.find(word, index + 1)
    if i == n - 1:
      break

  return string[index + len(word):]


def get_triples_from_lists(list1, list2, list3):
  triples = []
  for i in range(len(list1)):
    triple = {
      "title": list1[i],
      "caption": list2[i],
      "href": list3[i]
    }
    triples.append(triple)
  return triples

def triples_triples(triples):

  grouped_triples = []
  i = 0
  while i <= len(triples) - 3:
    triple_group = (triples[i], triples[i + 1], triples[i + 2])
    grouped_triples.append(triple_group)
    i = i + 1
  return grouped_triples

def related_entities_triples(start, end, kgr, lang, bi = True, file = True):
    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    browser = webdriver.Firefox(executable_path=r'C:\Program Files\Mozilla Firefox\gecko\geckodriver.exe', options=options)
    browser.get((f"https://www.sixdegreesofwikipedia.com/?source={start}&target={end}"))

    browser.find_element(By.CSS_SELECTOR, "button").click()
    div2 = False

    #wait = WebDriverWait(browser, 10)  # Adjust the timeout as needed
    #webtext = wait.until(EC.text_to_be_present_in_element_value((By.XPATH, "//div[1]/div[2]/div[5]"), "Individual paths"))
    #webtexto = webtext.text if webtext else "Text not found" 

    try:
        webtext = browser.find_elements(By.XPATH, "//div[1]/div[2]/div[5]")[0] 
        for _ in range(5):  # Scroll 5 times
            browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)  # Wait for content to load
        webtexto = webtext.text
        #if len(webtexto) < 20:
        #    div2 = True 
        #    response = requests.get(f"https://www.sixdegreesofwikipedia.com/?source={start}&target={end}")
        #    soup = bs(response.content, "html.parser")
        #    webtext = str(soup.text)
        if len(webtexto) < 80:
            div2 = True
            webtext = browser.find_elements(By.XPATH, "//div[1]/div[2]")[0] 
    except Exception as e:
        div2 = True
        webtext = browser.find_elements(By.XPATH, "//div[1]/div[2]")[0]
    #WebDriverWait(browser, 10).until(ec.text_to_be_present_in_element(webtext.text, "Individual paths"))
    
    #time.sleep(5)
    hrefs_list = []
    titles_list = []
    captions_list = []
    token = 0
    #time.sleep(5)
    #with open("webtext.txt", "w") as f:
    #        f.write(str(webtext.text))
    #with open("webtext.txt", "r") as f:
    #    webtexto = f.read()
    #f.close()
    #try:
    #    os.remove("C:/Users/Palma/Desktop/PHD/HILD&GARD/webtext.txt")
    #except OSError as e:
    #    print(e)

    #webtexto = webtext.text

    print(webtexto)
    if div2:
        try:
            ropes = delete_until_word(webtexto, "paths", 3)
        except Exception as e:
            ropes = delete_until_word(webtexto, "paths", 2)
    else:
        ropes = webtexto

    ropeslist = ropes.split("\n")
    if ropeslist[0] == '': ropeslist.remove('')
   
    for line in ropeslist:
        if ropeslist.index(line) % 2 != 1 and ropeslist.index(line) < len(ropeslist) - 1:
            titles_list.append(line)
            try:
                chref = browser.find_element(By.LINK_TEXT, line).get_property("href")
            except Exception as e:
                chref = "https://"+lang+".wikipedia.org/wiki/"+line.replace(" ", "_")               
        
            if kgr == "yago":
                chref = f"https://yago-knowledge.org/resource/yago:{line}"
            elif lang != "en" and lang != "de":
                chref = "https://"+str(lang)+ f"dbpedia.org/page/{line}"
            else:
                chref = f"https://dbpedia.org/page/{line}"
            hrefs_list.append(chref)
        else: pass
    print(hrefs_list)
    print(titles_list)


    if bi:
        browser.get((f"https://www.sixdegreesofwikipedia.com/?source={end}&target={start}"))

        browser.find_element(By.CSS_SELECTOR, "button").click()

        #time.sleep(15)
        div2 = False
        try:
            webtext = browser.find_elements(By.XPATH, "//div[1]/div[2]/div[5]")[0] 
            for _ in range(5):  # Scroll 10 times
                browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                time.sleep(1) 
            if len(webtext) < 20:
                div2 = True 
                response = requests.get(f"https://www.sixdegreesofwikipedia.com/?source={start}&target={end}")
                soup = bs(response.content, "html.parser")
                webtext = str(soup.text)
                if len(webtext) < 20:
                    webtext = browser.find_elements(By.XPATH, "//div[1]/div[2]")[0] 
        except Exception as e:
            webtext = browser.find_elements(By.XPATH, "//div[1]/div[2]")[0]

        time.sleep(5)
        hrefs_list = []
        titles_list = []
        captions_list = []
        token = 0

        webtexto = webtext.text
        #time.sleep(5)

        print(webtexto)

        if div2:
            try:
                ropes = delete_until_word(webtexto, "paths", 3)
            except Exception as e:
                ropes = delete_until_word(webtexto, "paths", 2)

        ropeslist = ropes.split("\n")
        if ropeslist[0] == '': ropeslist.remove('')
        for line in ropeslist:
            if ropeslist.index(line) % 2 != 1 and ropeslist.index(line) < len(ropeslist) - 1:
                titles_list.append(line)
                chref = browser.find_element(By.LINK_TEXT, line).get_property("href")

                if kgr == "yago":
                    chref = f"https://yago-knowledge.org/resource/yago:{line}"
                elif lang != "en" and lang != "de":
                    chref = "https://"+str(lang)+ f"dbpedia.org/page/{line}"
                else:
                    chref = f"https://dbpedia.org/page/{line}"
                hrefs_list.append(chref)
            else: pass
        print(hrefs_list)
        print(titles_list)

        for line in ropeslist:
            if ropeslist.index(line) % 2 == 1 and ropeslist.index(line) >= 1:
               captions_list.append(line)
        print(captions_list)


    for line in ropeslist:
        if ropeslist.index(line) % 2 == 1 and ropeslist.index(line) >= 1:
            captions_list.append(line)
    print(captions_list)

    triples = get_triples_from_lists(titles_list, captions_list, hrefs_list)
    print(triples)

    triplestriples = triples_triples(triples)

    if file == True:
        try:
            with open(f"C:\\Users\\Palma\\Desktop\\PHD\\DatasetThesis\\HildegardData\\{start}to{end}shortestpath_entities_triples.txt", "a") as f:
                f.write(str(triples))
                f.close()
        except Exception as e:
            pass
        try:
            with open(f"C:\\Users\\Palma\\Desktop\\PHD\\DatasetThesis\\HildegardData\\{start}to{end}shortestpath_relations_triples.txt", "a") as f:
                f.write(str(triplestriples))
                f.close()
        except Exception as e:
            pass

    browser.close()

    return triplestriples



# combos = [
# ('Honeymoon', 'Luxembourg'),
# ('Resistance movement', 'Historiography'),
# ('Social norm', 'Anschluss'),
# ('Wehrmacht', 'Symbol'),
# ('Technology', 'Society'),
# ('World War II', 'Bicycle'),
# ('Nazi Germany', 'Globalization')
# ]
 
# 'Resistance movement'; 'Historiography' 
# 'Social norm'; 'Anschluss' 
# 'Wehrmacht'; 'Symbol'
#  'Technology'; 'Society'
#  'Freedom of the press'; 'Forced labour'
#  'Honeymoon'; 'Luxembourg' ]
# 'World War II'; 'Bicycle' 
# 'Nazi Germany'; 'Globalization' 
# 'Resistance movement'; 'Historiography' 
# 'Social norm'; 'Anschluss' 
# 'Wehrmacht'; 'Symbol'
#  'Technology'; 'Society'
#  'Freedom of the press'; 'Forced labour'
#  'Honeymoon'; 'Luxembourg' 

# for ele in combos:
#     start_page = str(ele[0])
#     end_page = str(ele[1])
#     shortest_path = related_entities_triples(start_page, end_page, "dbpedia", "en", False, True)
#     print(shortest_path)