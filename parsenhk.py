#!/bin/python

from bs4 import BeautifulSoup
import json
from datetime import datetime
import requests
import os

DEBUG=True
#dateselector= datetime.now().strftime('%Y%m%d')
dateselector= datetime.now().strftime('%Y%m')
#file_path = 'new.html'
source='https://k.nhk.jp/knews/cat4_00.html'
nhknewsroot='https://k.nhk.jp/knews'
archivedir='Feeds'


def debug(text):
  if DEBUG == True:
    print('DEBUG '+str(text))

def url_get(url):
  try:
    response = requests.get(url)
    response.raise_for_status()  # Vérifie les erreurs
  except requests.exceptions.HTTPError as http_err:
    print(f"Erreur HTTP: {http_err}")
    exit(9)
  html_content = response.text
  return html_content




def url_to_json(url):
    #with open(file_path, 'r', encoding='shift_jis') as file:
    #    html_content = file.read()

    try:
      response = requests.get(url)
      response.raise_for_status()  # Vérifie les erreurs
    except requests.exceptions.HTTPError as http_err:
      print(f"Erreur HTTP: {http_err}")
      exit(9)
    html_content = response.text

    # Analyse le contenu HTML avec BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Dictionnaire pour stocker les données en JSON
    data = {}
    
    # Extrait les informations spécifiques
    data['title'] = soup.title.string if soup.title else 'No title'
    data['paragraphs'] = [p.get_text(strip=True) for p in soup.find_all('p')]
    data['links'] = [{'text': a.get_text(strip=True), 'href': a.get('href')} for a in soup.find_all('a', href=True)]
    
    # Convertit le dictionnaire en JSON
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    return json_data

def url_to_file(url,archdir=nhknewsroot):
  #20241030/k10014623161000.html
  geturl='{}/{}'.format(nhknewsroot,url) 
  text=url_get(geturl)
  html=url.split('/')[1]
  datedir="{}/{}".format(archdir,url.split('/')[0])
  for d in archdir,datedir:
    if not os.path.exists(d):
        os.makedirs(d)
        debug("Creating {}".format(d))
    else:
        debug("dir {} exists".format(d))
  with open(html, "w") as file:
    print('Write {}'.format(html))
    file.write(text)
# main
json_result = url_to_json(source)
j=json.loads(json_result)
#debug(j['links'])
for html in j['links']:
  t=html['text']
  h=html['href']
  selector=len(dateselector)
  if h.split('/')[0][0:selector] == dateselector:
    #print(h)
    url_to_file(h)
