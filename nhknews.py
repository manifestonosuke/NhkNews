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
import signal



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

parser = argparse.ArgumentParser(description="Program to get NHK news podcast.\nWithout argument will get all files.",formatter_class=RawTextHelpFormatter)
parser.add_argument('-a','--audio',action="store_true",help='grab audio only')
parser.add_argument('-d','--debug',action="store_true",help='debug mode')
parser.add_argument('-f','--force',action="store_true",help='force re-downloading existing files')
parser.add_argument('--sjis',action="store_true",help='the script reencode html in utf-8 use this otption if you want alsoi keep sjis file (named .html.sjis)')
parser.add_argument('-t','--text',action="store_true",help='Grab text only')
parser.add_argument('-T','--time',help='If audio is chosen select time to limit download time of the day between  0 to 24')
args,noargs  = parser.parse_known_args()
if args.debug==True:
  display.set('debug')

dateselector= datetime.now().strftime('%Y%m')
source='https://www.nhk.or.jp/s-media/news/podcast/list/v1/all.xml'
seiji='https://k.nhk.jp/knews/cat4_00.html'
knewssection={1:"社会",2:"暮らし",3:"科学・文化",4:"政治",5:"ビジネス",6:"国際",7:"スポーツ",8:"気象",9:"地域"}
knewsroot='https://k.nhk.jp/knews/'
knewsneed=[1,2,3,4,5,6,9]
nhknewsroot='https://k.nhk.jp/knews'
feeddir='NhkFeeds'
archivedir='{}/{}'.format(os.environ['HOME'],feeddir)
wanted=""
idxsave='/tmp/nhkindex.dict'

def handler(signum, frame):
  display.info("然らば")
  exit(0)

signal.signal(signal.SIGINT, handler)

#def url_get(url,archive=False,archivepath='/dev/null',bin=False,mp3tag=None):
def url_get(url,bin=False):
  display.info("Grabbing {}".format(url))
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
  if coding != None:
    display.debug("Done (encoding {})".format(coding))
  response.encoding = response.apparent_encoding
  if bin:
    html_content = response.content
  else:
    html_content = response.text
  display.debug("return code {} data length {}".format(response.status_code,len(response.content)))
  return html_content
  
def data_to_file(data,archive,bin=False):
  openopt='w'
  if bin == False:
    openopt='wb'
  try:
    file=open(archive,openopt)
  except:
    display.error("Can not open archive file {}".format(archive))
    exit(9)
  else:
    display.info("writing {} as {}".format(archive,openopt))
    file.write(data)
  return 0

def tag_file(archive,mp3tag):
  display.debug("Adding tag {} to {}".format(mp3tag,archive))
  audio = eyed3.load(archive)
  if audio.tag is None:
    audio.initTag()
  audio.tag.title = mp3tag
  audio.tag.composer = "NHKラジオニュース" 
  audio.tag.language = "Japanese"
  audio.tag.version = (2, 3, 0) 
  audio.tag.save(encoding='utf-16')
  return True

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

def url_to_file(url,title=None,archdir=archivedir):
  #20241030/k10014623161000.html
  display.debug("Enter url_to_file {}".format(url))
  geturl='{}/{}'.format(nhknewsroot,url) 
  html_content=url_get(geturl)
  html=url.split('/')[1]
  datedir="{}/{}".format(archdir,url.split('/')[0])
  if title != None:
    outputfile="{}/{}".format(datedir,title)
  else:
    outputfile="{}/{}".format(datedir,html)
  if os.path.exists(outputfile):
    if args.force != True:
      display.info("Skipping file {} exist".format(outputfile))
      return True 
  for d in archdir,datedir:
    if not os.path.exists(d):
        os.makedirs(d)
        display.debug("Creating {}".format(d))
  if args.sjis == True:
    sjis=outputfile+'.sjis'
    with open(sjis, "w", encoding='SHIFT_JIS') as file:
      display.info('Write sjis {}'.format(sjis))
      file.write(html_content)
      file.close()
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
    if t[0] == '･':
      t=t[1:]
    t="{}.html".format(t)
    selector=len(dateselector)
    if h.split('/')[0][0:selector] == dateselector:
      url_to_file(h,t)

def time_4_digits(value):
  display.debug("hour digit {}".format(value))
  if int(value) > 24 or int(value) < 0:
    display.error("time must be between 1 to 24",fatal=True)
  if len(str(value)) == 1:
    twodigit='0'+str(value)
  else:
    twodigit=value
  display.debug("chosen time for audio {}".format(twodigit))
  return twodigit

def get_audio_content(url,hour):
  #idx_contents=url_get(url,archive=True,archivepath=idxsave)
  idx_contents=url_get(url)
  json_data=xml_to_json(idx_contents)
  items=json_data['rss']['channel']['item']
  found=0
  for i in items:
    pubdate=i['pubDate'].split(',')[1:][0].split()
    display.debug("grad audio date {}".format(pubdate))
    pubdate[1]=datetime.strptime(pubdate[1], '%b').month
    pubtime=pubdate[3]
    pubhour=pubtime.split(':')[0]
    title=i['title'].split()
    title_date=title[0]
    title_time=title[1]
    date_number=title_time.split('時')[0][2:]
    if hour != None:
      hour=time_4_digits(hour)
      display.debug("checking audio time {} {}".format(hour,title_time))
      if hour != pubhour:
        display.verbose("Skipping hour {} because differ {}".format(hour,pubhour))
        continue
    else:
      print("any {}".format(title_time))
    url=i['enclosure']['@url']
    #mp3_title=url.split('/')[-1]
    mp3_title='{}.{}'.format(title_time,'mp3')
    path="{}/{}{:02d}{}/{}".format(archivedir,pubdate[2],pubdate[1],pubdate[0],mp3_title)
    if os.path.exists(path):
      if args.force != True:
        display.info("File {} already exist skipping".format(path))
        continue
      else:
        display.debug("File {} already, force option overwritting".format(path))
    display.debug("[{}h] {} Pubdate {} Title : {} \n --> Url : {}".format(pubhour,title_time,path,title,url))
    response=url_get(url,bin=True)
    data_to_file(response,path)
    tag_file(path,title_time)
  
def main():
  display.debug("Args : {}".format(args))
  if args.audio == False and args.text == False:
    args.audio=True
    args.text=True
  if args.text:
    for i in knewsneed:
#seiji='https://k.nhk.jp/knews/cat4_00.html'
#knewssection={1:"社会",2:"暮らし",3:"科学・文化",4:"政治",5:"ビジネス",6:"国際",7:"スポーツ",8:"気象",9:"地域"}
#knewsroot='https://k.nhk.jp/knews/'
      url="https://k.nhk.jp/knews/cat{}_00.html".format(i) 
      display.debug("Getting section {}".format(knewssection[1]))
      get_html_content(url)
  if args.audio:
    get_audio_content(source,args.time)

if __name__ == '__main__':
  main()
else:  
  print("LOADED")

