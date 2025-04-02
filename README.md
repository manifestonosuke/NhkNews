# Purpose

Script to get podcast and text from NHK News

# Files
The is a single script getting both mp3 and text.
```
$ ./nhknews.py -h
usage: nhknews.py [-h] [-a] [-d] [-t]

Program to get NHK news podcast
Without argument will get all files.

options:
  -h, --help   show this help message and exit
  -a, --audio  Grad audio only
  -d, --debug  debug mode
  -t, --text   Grad text only

```
Other files are usually test.

# Archive location 
The directory where the file are stored is HC in this 2 variables, which is ~/NhkFeeds :
```
feeddir='NhkFeeds'
archivedir='{}/{}'.format(os.environ['HOME'],feeddir)
``` 

# General 仕組み
## Text
The articles are sorted in type like 社会, 政治 in prefixed by url https://k.nhk.jp/knews/. The type is defined by a category like cat4_00.html for 政治.
The script now only download this type manage by this variable.
seiji='https://k.nhk.jp/knews/cat4_00.html'
The script then convert htmlto json and get the href containing the path in the variable **nhknewsroot** 

## Podcast
The pod cast are defined in a xml files : 
```
source='https://www.nhk.or.jp/s-media/news/podcast/list/v1/all.xml'
```
From the xml all mp3 files location and title are defined. Mp3 files are downloaded, sorted in a subdir with the date and eyed3 tagged with the title 
```
[pierre@Manjaro NhkFeeds]$ eyeD3 ./20241104/e38b605f610b15b877e9e9a215a001e8_64k.mp3 
/data/home/pierre/NhkFeeds/20241104/e38b605f610b15b877e9e9a215a001e8_64k.mp3                                                                                 [ 6.87 MB ]
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Time: 15:00     MPEG1, Layer III        [ 64 kb/s @ 48000 Hz - Stereo ]
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ID3 v2.3:
title: 午前７時のNHKニュース
artist: 
album: 
composer: NHKラジオニュース
```

## Python deps 

```
python-beautifulsoup4
python-xmltodict
python-eyed3
```

