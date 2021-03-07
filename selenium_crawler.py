# -*- coding: utf-8 -*-
"""
Created on Thu May 21 18:05:12 2020

@author: Ash
"""
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from time import gmtime, strftime
from pathlib import Path
import re
import datetime
import webbrowser
from time import sleep
from requests import Session
from robobrowser import RoboBrowser
from lxml import html
from urllib import parse
import timestring
import json
import requests
from requests.auth import HTTPBasicAuth
import logging
import os
import CONFIG
from bs4 import BeautifulSoup


#CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"
#GOOGLE_CHROME_BIN = "/app/.apt/usr/bin/google-chrome"

CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
GOOGLE_CHROME_BIN = "/usr/bin/google-chrome"


option = webdriver.ChromeOptions()
#option.binary_location = GOOGLE_CHROME_BIN
option.add_argument("--headless")  
option.add_argument("--disable-dev-shm-usage")
option.add_argument("--no-sandbox")
option.add_argument('--disable-gpu')
option.add_argument("--incognito")


browser = webdriver.Chrome(executable_path=r"D:\software\chromedriver", chrome_options=option)
#browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,  chrome_options=option)
def checkTicket(eventId):
    try:
        print('checking ticket')
        url = "https://mobile.facebook.com/events/"+str(eventId)
        #browser = webdriver.Chrome(executable_path=r"D:\software\chromedriver", chrome_options=option)
        
        browser.get(url)
        time.sleep(5)
        soup = BeautifulSoup(browser.page_source, 'lxml')
        print('sleep ends')
        x = 0
        for line in soup.find_all('section',attrs={"id" : "event_summary"}):
            l = line.find_all('div')
            for e in l:
                if("Tickets" in e.text):
                    x += 1
        d = []
        for line in soup.find_all('div', attrs={"id":"unit_id_703958566405594"}):
            l = line.find_all('a')
            for e in l:
                if(e.text!=''):
                    d.append(e.text)
        b = True
        if(x > 0):
            b = True
            d.append(True)
        else:
            b = False
            d.append(False)
        print(d)
        if len(d) == 3:
            return d
        else:
            return [0,0,b]
    except Exception as e: # Catch failture
        print('\nGetevent error' + str(e))
        return [0,0,True]

   
   
def sele_login(eventid):
    print('Logging in to facebook...')
    browser.get("https://mobile.facebook.com") # Facebook profile's language need to be EN-US!
    try:
        login_form = browser.find_element_by_id('login_form')
        #login_form['email'].value = CONFIG.FB_EMAIL
        #login_form['pass'].value = CONFIG.FB_PASSWORD
        username = browser.find_element_by_name('email')
        username.send_keys(CONFIG.FB_EMAIL)
        
        password = browser.find_element_by_name('pass')
        password.send_keys(CONFIG.FB_PASSWORD)
        login_form.submit()
        i = checkTicket(eventid)
        print(i)
    except Exception as e:
        if(type(e).__name__=='NoSuchElementException'):
            i = checkTicket(eventid)
            print(i)
        else:
            print(type(e).__name__)
    
    #browser.quit()
#login()


    '''
    print(locationName.text + ' ' + locationSoup.text)
    print(locationSoup.text)
    links_with_text = [a['href'] for a in line.find_all('a', href=True) if a.text]
    print(links_with_text)
    link = []
    for i in links_with_text:
        lnk = ''
        t1 = i.split('&h=')
        t2 = t1[0].split('?u=')
        lnk = t2[1].replace('%3A',':')
        lnk = lnk.replace('%2F','/')
        link.append(lnk)
    for i in link:
        print(i)
    '''
    
'''    
for line in soup.find_all('div',attrs={"class" : "coronavirus-statistics"}):
    print(line.text)
''' 
def closeBrowser():
    browser.close()


     
    