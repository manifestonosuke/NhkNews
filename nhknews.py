#!/bin/python
###dd# -*- coding: utf-8 -*-

from datetime import datetime
import argparse
from argparse import RawTextHelpFormatter
import xmltodict
import unicodedata
import requests
import os
from bs4 import BeautifulSoup as bs
import json
import eyed3

class Msg():
  def __init__(self,level='info'):
    self.level=level
    self.valid=['info','debug','verbose','warning']

  def set(self,level):
    print("{0:15} : {1}".format('INFO','Setting loglevel to '+level))
    if level not in self.valid:
      self.display("not a valid level {0}".format(level))
      return(9)
    self.level=level

  def verbose(self,msg,label=None):
    if self.level == 'verbose' :
      if label != None:
        header=label
      else:
        header='VERBOSE'
      print("{0:15} : {1}".format(header,msg))

  def info(self,msg,label=None):
    if label != None:
      header=label
    else:
      header="INFO"
    print("{0:15} : {1}".format(header,msg))

  def error(self,msg,fatal=False):
    header="ERROR"
    print("{0:15} : {1}".format(header,msg))
    if fatal:
      exit(9)

  def warning(self,msg,fatal=False):
    header="WARNING"
    print("{0:15} : {1}".format(header,msg))
    if fatal:
      exit(9)

  def debug(self,msg):
    if self.level == "debug":
      header="DEBUG"
      print("{0:15} : {1}".format(header,msg))

  def raw(self,msg):
      print("{0}".format(msg))
  def showlevel(self):
    print("Error level is {0} : ".format(self.level))
display=Msg('info')

parser = argparse.ArgumentParser(description="Program to get NHK news podcast",formatter_class=RawTextHelpFormatter)
parser.add_argument('-a','--audio',action="store_true",help='Grad audio only')
parser.add_argument('-d','--debug',action="store_true",help='debug mode')
parser.add_argument('-t','--text',action="store_true",help='Grad text only')
args,noargs  = parser.parse_known_args()
if args.debug==True:
  display.set('debug')

dateselector= datetime.now().strftime('%Y%m')
source='https://www.nhk.or.jp/s-media/news/podcast/list/v1/all.xml'
seiji='https://k.nhk.jp/knews/cat4_00.html'
nhknewsroot='https://k.nhk.jp/knews'
feeddir='NhkFeeds'
archivedir='{}/{}'.format(os.environ['HOME'],feeddir)
wanted=""
rawdata='/tmp/nhkindex.dict'

def url_get(url,archive=False,archivepath='/dev/null',bin=False,mp3tag=None):
  if bin == True:
    openopt='wb'
  else:
    openopt='w'
  try:
    response = requests.get(url)
    response.raise_for_status()  # Vérifie les erreurs
  except Exception as http_err:
    display.error("Erreur HTTP: {}".format(http_err),fatal=True)
    exit(9)
  coding=response.apparent_encoding
  display.info("Grabbing {} (encoding {})".format(url,coding))
  response.encoding = response.apparent_encoding
  if bin:
    html_content = response.content
  else:
    html_content = response.text
  if archive:
    try:
      file=open(archivepath,openopt) 
    except:
      display.error("Can not open archive file {}".format(rawdata))
    else:
      display.info("writing {} as {}".format(archivepath,openopt))
      file.write(html_content)
      file.close()
      if mp3tag != None:
        display.debug("Adding tag {} to {}".format(mp3tag,archivepath))
        #audio = EasyID3(archivepath)
        #audio = MP3(archivepath)
        audio = eyed3.load(archivepath)
        if audio.tag is None:
          #audio.add_tags()
          audio.initTag()
        audio.tag.title = mp3tag
        audio.tag.composer = "NHKラジオニュース" 
        audio.tag.language = "Japanese"
        audio.tag.version = (2, 3, 0) 
        audio.tag.save(encoding='utf-16')
        # Sauvegarde des modifications
        audio.tag.save(encoding='utf-16')
        #audio.tags.add(TIT1(encoding=1, text="NHKラジオニュース"))
        #audio.tags.add(TIT2(encoding=1, text=mp3tag.encode('utf-16').decode('utf-16')))
        #audio.tags.add(TIT3(encoding=1, text='du bon viel ascii'))
        #audio['title']=mp3tag
        #audio.save(v2_version=3)
  return html_content

def xml_to_json(contents):
  json_data=data_dict = xmltodict.parse(contents) 
  return json_data

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
        display.debug("Creating {}".format(d))
    else:
        display.debug("dir {} exists".format(d))
  sjis=outputfile+'.sjis'
  with open(sjis, "w", encoding='SHIFT_JIS') as file:
    display.info('Write sjis {}'.format(sjis))
    file.write(html_content)
    file.close()
  #<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS">
  with open(outputfile, "w", encoding='utf-8') as file:
    soup = bs(html_content,'html.parser')
    modified=soup.find("meta", content="text/html; charset=Shift_JIS")
    modified['content']='text/html; charset=utf-8'
    display.info('Write utf8 {}'.format(outputfile))
    file.write(str(soup))

def get_html_content(url):
  json_result = url_to_json(url)
  j=json.loads(json_result)
  for html in j['links']:
    t=html['text']
    h=html['href']
    selector=len(dateselector)
    if h.split('/')[0][0:selector] == dateselector:
      url_to_file(h)

def get_audio_content(url):
  idx_contents=url_get(url,archive=True,archivepath=rawdata)
  json_data=xml_to_json(idx_contents)
  items=json_data['rss']['channel']['item']
  found=0
  for i in items:
    pubdate=i['pubDate'].split(',')[1:][0].split()
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
    display.debug("[{}h] {} Pubdate {} Title : {} \n --> Url : {}".format(pubhour,title_time,path,title,url))
    response=url_get(url,archive=True,archivepath=path,bin=True,mp3tag=title_time)
  
def main():
  display.debug("Args : {}".format(args))
  if args.audio == False and args.text == False:
    print('A')
    exit()
    args.audio=True
    args.text=True
  if args.text:
    get_html_content(seiji)
  if args.audio:
    get_audio_content(source)

if __name__ == '__main__':
  main()
else:  
  print("LOADED")

