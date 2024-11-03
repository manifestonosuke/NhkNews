#!/bin/python


from datetime import datetime
import argparse
from argparse import RawTextHelpFormatter
import xmltodict
import unicodedata
import requests
import os

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

parser = argparse.ArgumentParser(description="このプログラムの説明.\nUse a csv file from anki with 2 kanjis per card forming words. Vocabulary list can also be checked for given kanjis.\nBase syntax kanala.py <anki csv file> [args] kanjis. For -w option anki file not needed",formatter_class=RawTextHelpFormatter)
parser.add_argument('-d','--debug',action="store_true",help='debug mode')
args,noargs  = parser.parse_known_args()
if args.debug==True:
  display.set('debug')

dateselector= datetime.now().strftime('%Y%m')
source='https://www.nhk.or.jp/s-media/news/podcast/list/v1/all.xml'
nhknewsroot='https://k.nhk.jp/knews'
archivedir='Feeds'
wanted=""
rawdata='/tmp/nhkindex.dict'

def url_get(url,archive=False,archivepath='/dev/null',bin=False,mp3tag=None):
  if mp3tag:
    exit()
  if bin == True:
    openopt='wb'
  else:
    openopt='w'
  display.info("Retrieving {}".format(url))
  try:
    response = requests.get(url)
    response.raise_for_status()  # Vérifie les erreurs
  except Exception as http_err:
    display.error("Erreur HTTP: {}".format(http_err),fatal=True)
    exit(9)
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
  response=url_get(url,archive=True,archivepath=path,bin=True)
  

