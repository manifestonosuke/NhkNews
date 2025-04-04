#!/bin/python
###dd# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
import requests
import os

DEBUG=False
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
  except Exception as http_err:
    print(f"Erreur HTTP: {http_err}")
    exit(9)
  coding=response.apparent_encoding
  print("Grabbing {} (encoding {})".format(url,coding))
  response.encoding = response.apparent_encoding
  html_content = response.text
  return html_content




def url_to_json(url):
    html_content=url_get(url)
    # Analyse le contenu HTML avec BeautifulSoup
    soup = bs(html_content, 'html.parser')
    
    # Dictionnaire pour stocker les données en JSON
    data = {}
    
    # Extrait les informations spécifiques
    data['title'] = soup.title.string if soup.title else 'No title'
    data['paragraphs'] = [p.get_text(strip=True) for p in soup.find_all('p')]
    data['links'] = [{'text': a.get_text(strip=True), 'href': a.get('href')} for a in soup.find_all('a', href=True)]
    
    # Convertit le dictionnaire en JSON
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    return json_data

def url_to_file(url,archdir=archivedir):
  #20241030/k10014623161000.html
  geturl='{}/{}'.format(nhknewsroot,url) 
  html_content=url_get(geturl)
  html=url.split('/')[1]
  datedir="{}/{}".format(archdir,url.split('/')[0])
  outputfile="{}/{}".format(datedir,html)
  for d in archdir,datedir:
    if not os.path.exists(d):
        os.makedirs(d)
        debug("Creating {}".format(d))
    else:
        debug("dir {} exists".format(d))
  sjis=outputfile+'.sjis'
  with open(sjis, "w", encoding='SHIFT_JIS') as file:
    print('Write {}'.format(outputfile))
    file.write(html_content)
    file.close()
  #<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">
  with open(outputfile, "w", encoding='utf-8') as file:
    soup = bs(html_content,'html.parser')
    modified=soup.find("meta", content="text/html; charset=Shift_JIS")
    modified['content']='text/html; charset=utf-8'
    print('Write utf8 {}'.format(outputfile))
    file.write(str(soup))
# main
json_result = url_to_json(source)
j=json.loads(json_result)
for html in j['links']:
  t=html['text']
  h=html['href']
  selector=len(dateselector)
  if h.split('/')[0][0:selector] == dateselector:
    url_to_file(h)
