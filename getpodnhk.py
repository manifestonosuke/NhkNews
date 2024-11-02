#!/bin/python


from datetime import datetime
import xmltodict
import unicodedata
import requests
import os

DEBUG=True
dateselector= datetime.now().strftime('%Y%m')
source='https://www.nhk.or.jp/s-media/news/podcast/list/v1/all.xml'
nhknewsroot='https://k.nhk.jp/knews'
archivedir='Feeds'
wanted=""
rawdata='/tmp/nhkindex.dict'

def debug(text):
  if DEBUG == True:
    print('DEBUG '+str(text))

def url_get(url,archive=False,archivepath='/dev/null'):
  print("Retrieving {}".format(url))
  try:
    response = requests.get(url)
    response.raise_for_status()  # Vérifie les erreurs
  except Exception as http_err:
    print(f"Erreur HTTP: {http_err}")
    exit(9)
  html_content = response.text
  if archive:
    try:
      file=open(archivepath,"w") 
    except:
      print("Can not open archive file {}".format(rawdata))
    else:
      print("writing {}".format(archivepath))
      file.write(html_content)
  return html_content

def xml_to_json(contents):
  json_data=data_dict = xmltodict.parse(contents) 
  return json_data

def url_to_file(url,archdir=archivedir):
  #20241030/k10014623161000.html
  geturl='{}/{}'.format(nhknewsroot,url) 
  text=url_get(geturl)
  html=url.split('/')[1]
  datedir="{}/{}".format(archdir,url.split('/')[0])
  outputfile="{}/{}".format(datedir,html)
  for d in archdir,datedir:
    if not os.path.exists(d):
        os.makedirs(d)
        debug("Creating {}".format(d))
    else:
        debug("dir {} exists".format(d))
  with open(outputfile, "w") as file:
    print('Write {}'.format(html))
    file.write(text)

## 
idx_contents=url_get(source,archive=True,archivepath=rawdata)
json_data=xml_to_json(idx_contents)
items=json_data['rss']['channel']['item']
found=0
for i in items:
  pubdate=i['pubDate'].split(',')[1:][0].split()
  #print(pubdate)
  pubdate[1]=datetime.strptime(pubdate[1], '%b').month
  pubtime=pubdate[3]
  pubhour=pubtime.split(':')[0]
  title=i['title'].split()
  title_date=title[0]
  title_time=title[1]
  date_number=title_time.split('時')[0][2:]
  url=i['enclosure']['@url']
  mp3_title=url.split('/')[-1]
  path="{}/{}{}{}/{}".format(archivedir,pubdate[2],pubdate[1],pubdate[0],mp3_title)
  #print("[{}] Pubdate {} Title : {} \n Url : {}".format(pubhour,path,title,url))
  response=url_get(url,archive=True,archivepath=path)
  

