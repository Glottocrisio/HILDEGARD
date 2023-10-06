import requests
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time

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


def delete_until_given_instance_of_word_in_string(string, word, n):

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

def related_entities_triples(start, end, bi = True, file = True):
    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    browser = webdriver.Firefox(executable_path=r'C:\Program Files\Mozilla Firefox\gecko\geckodriver.exe', options=options)
    #?source=Alexander the Great&target=Bible
    browser.get((f"https://www.sixdegreesofwikipedia.com/?source={start}&target={end}"))

    browser.find_element(By.CSS_SELECTOR, "button").click()

    time.sleep(7)
    webtext = browser.find_elements(By.XPATH, "//div[1]/div[2]")[0]
    webtext.text
    time.sleep(5)
    hrefs_list = []
    titles_list = []
    captions_list = []
    token = 0
    time.sleep(5)
    webtexto = webtext.text
    time.sleep(5)

    print(webtexto)

    ropes = delete_until_given_instance_of_word_in_string(webtexto, "paths", 3)

    ropeslist = ropes.split("\n")
   
    for line in ropeslist:
        if ropeslist.index(line) % 2 == 1 and ropeslist.index(line) < len(ropeslist) - 1:
            titles_list.append(line)
            try:
                chref = browser.find_element(By.LINK_TEXT, line).get_property("href")
                hrefs_list.append(chref)
            except Exception as e:
                chref = f"https://en.wikipedia.org/wiki/{line}"
                hrefs_list.append(chref)
        else: pass
    print(hrefs_list)
    print(titles_list)


    if bi:
        browser.get((f"https://www.sixdegreesofwikipedia.com/?source={end}&target={start}"))

        browser.find_element(By.CSS_SELECTOR, "button").click()

        time.sleep(15)
        webtext = browser.find_elements(By.XPATH, "//div[1]/div[2]")[0]
        webtext.text
        time.sleep(5)
        hrefs_list = []
        titles_list = []
        captions_list = []
        token = 0
        webtexto = webtext.text
        time.sleep(5)

        print(webtexto)

        ropes = delete_until_given_instance_of_word_in_string(webtexto, "paths", 3)

        ropeslist = ropes.split("\n")
   
        for line in ropeslist:
            if ropeslist.index(line) % 2 == 1 and ropeslist.index(line) < len(ropeslist) - 1:
                titles_list.append(line)
                try:
                    chref = browser.find_element(By.LINK_TEXT, line).get_property("href")
                    hrefs_list.append(chref)
                except Exception as e:
                    chref = f"https://en.wikipedia.org/wiki/{line}"
                    hrefs_list.append(chref)
            else: pass
        print(hrefs_list)
        print(titles_list)

        for line in ropeslist:
            if ropeslist.index(line) % 2 != 1 and ropeslist.index(line) > 1:
               captions_list.append(line)
        print(captions_list)



    for line in ropeslist:
        if ropeslist.index(line) % 2 != 1 and ropeslist.index(line) > 1:
            captions_list.append(line)
    print(captions_list)

    triples = get_triples_from_lists(titles_list, captions_list, hrefs_list)
    print(triples)

    triplestriples = triples_triples(triples)

    if file == True:

        with open(f"{start}to{end}shortestpath_entities_triples.txt", "a") as f:
            f.write(str(triples))
            f.close()

        with open(f"{start}to{end}shortestpath_relations_triples.txt", "a") as f:
            f.write(str(triplestriples))
            f.close()

    browser.close()

    return triplestriples
