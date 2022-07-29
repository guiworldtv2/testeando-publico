#### NOTES
# please keep in mind that this will create a directory "videos" in the 
# current working directory



import pandas as pd
import numpy as np
import requests
import praw
import pprint
import pytube
from pytube import YouTube
import urllib.request
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from chromedriver_py import binary_path
import os
import time

#print('hello')
filename = os.getcwd()+'\\videos'
os.makedirs(filename, exist_ok=True)

reddit = praw.Reddit(
     client_id="sVYvodt7Z20Wvg",
     client_secret="KlFb6tNGGDCNLY_ZmFbNJu6Gbllrlw",
     user_agent="script:timelapsegrowery_scraper:v1 (by /u/owling101)"
 )
#print(reddit.read_only)

youtube = []
vreddit = []
vimeo = []
gfycat = []
imgur = [] # leaving these out for now
for submission in reddit.subreddit('timelapsegrowery').top(time_filter='all', limit=None):
    #print(submission.title)
    if 'v.redd' in submission.url:
        vreddit.append(submission.url)
    elif 'youtu' in submission.url:
        youtube.append(submission.url)
    elif 'imgur' in submission.url:
        imgur.append(submission.url)
    elif 'vimeo' in submission.url:
        vimeo.append(submission.url)
    elif 'gfycat' in submission.url:
        gfycat.append(submission.url)

imgur.pop(3) # photo
# print(len(youtube))
# print(youtube)
# print()
# print()
# print(len(vreddit))
# print(vreddit)
# print()
# print()
# print(len(vimeo))
# print(vimeo)
# print()
# print()
# print(len(gfycat))
# print(gfycat)
# print()
# print()
# print(len(imgur))
# print(imgur)


# downloading vreddit
for idx, i in enumerate(vreddit):
	print('vreddit_'+str(idx))
	try:
	    urllib.request.urlretrieve(i+'/DASH_1080.mp4?source=fallback', filename+'\\'+'vreddit_'+str(idx)+'.mp4')
	except:
	    driver = webdriver.Chrome(executable_path=binary_path)
	    driver.get("https://viddit.red/")
	    #time.sleep(2)
	    form = driver.find_element_by_name('url')
	    form.send_keys(i)
	    form.send_keys(Keys.RETURN)
	    #time.sleep(2)
	    vid = driver.find_element_by_id('dlbutton')
	    link = vid.get_attribute('href')
	    driver.close()
	    urllib.request.urlretrieve(link, filename+'\\'+'vreddit_'+str(idx)+'.mp4')


# downloading vimeo
for idx, i in enumerate(vimeo):
	print('vimeo_'+str(idx))
	vidUrls = []
	driver = webdriver.Chrome(executable_path=binary_path)
	driver.get("https://vimeo-downloader.com/")
	form = driver.find_element_by_name('url')
	form.send_keys(i)
	form.send_keys(Keys.RETURN)
	vid = driver.find_element_by_xpath('//source')
	link = vid.get_attribute('src')
	driver.close()
	urllib.request.urlretrieve(link, filename+'\\'+'vimeo_'+str(idx)+'.mp4')



# downloading gfycat
for idx, i in enumerate(gfycat):
	print('gfycat_'+str(idx))
	response = requests.get(i)
	page = response.text
	soup = BeautifulSoup(page, 'lxml')
	link = soup.findAll(type='video/mp4')[1].get('src')
	urllib.request.urlretrieve(link, filename+'\\'+'gfycat_'+str(idx)+'.mp4')


# downloading imgur
for idx, i in enumerate(imgur):
	print('imgur_'+str(idx))
	if 'i.imgur' not in i: # fairly time consuming for only 5 vids, this can be skipped w/ the continue
	    driver = webdriver.Chrome(executable_path=binary_path)
	    driver.get(i)
	    #time.sleep(2)
	    vid = driver.find_element_by_xpath('//source')
	    vidLink = vid.get_attribute('src')
	    driver.close()
	    urllib.request.urlretrieve(vidLink, filename+'\\'+'imgur_'+str(idx)+'.mp4')
	else:
		urllib.request.urlretrieve(i, filename+'\\'+'imgur_'+str(idx)+'.mp4')


# downloading youtube

# not great with pytube, and using selenium is annoying because of 
# ad popups on most sites, would recommend manually downloading failed yt vids
# http://ytmp3.cc/ is a good place

fails = []
for idx, i in enumerate(youtube):
	print('youtube'+str(idx))
	splitI = i.split('/')
	newLink = splitI[0]+'//'+'www.youtube.com/watch?v='+splitI[3]
	try:
	    streams = YouTube(newLink).streams.filter(only_video=True)
	except Exception as e:
	    print(e)
	    streams = []
	    fails.append(i)
	for j in streams:
	    try:
	        j.download(os.getcwd()+'\\vids')
	        break
	    except Exception as f:
	        print(f)
	        continue 
print(fails)
