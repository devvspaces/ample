import datetime
import webbrowser
from time import sleep
from requests import Session
from robobrowser import RoboBrowser
from lxml import html, etree
from urllib import parse
import timestring
import json
import requests
from requests.auth import HTTPBasicAuth
import logging
import os.path
import CONFIG
from db import get_db, query_db, upsert_db
from selenium_crawler import checkTicket, sele_login, closeBrowser
from geopy.geocoders import Nominatim
from dateutil.parser import parse
from itertools import chain
import xml.dom.minidom
import time

from min_img import gei
# from apscheduler.schedulers.blocking import BlockingScheduler

# sched = BlockingScheduler()



# Create the logger and set the logging level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create the logger for errors only
logger2 = logging.getLogger('Crawler Errors')
logger2.setLevel(logging.WARNING)


# Create formatter
formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")


# Create file handler
file_handler = logging.FileHandler('crawler_info.log')
# Add formatter to the file handler
file_handler.setFormatter(formatter)


# Create file handler
file_handler2 = logging.FileHandler('crawler_errors.log')
# Add formatter to the file handler
file_handler2.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)
logger2.addHandler(file_handler2)





abominations = ['\'','\"']

# Convenience functions
def replace_syntax(text):
    try:
        new_text = ''
        if text and type(text).__name__=='str':
            for i in text:
                if i in abominations:
                    new_text+='-'
                else:
                    new_text+=i
            return new_text
    except Exception as e:
        logger2.warning('This text syntax was tried to be replaced: '+str(text))
        logger2.exception(e)

    return text


""" headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'}
proxies = {'https': 'https://88.209.225.150:53281', 'http': 'http://88.209.225.150:53281'} """
file = 'del.html'
mapurl = "https://maps.googleapis.com/maps/api/place/textsearch/json?key=AIzaSyAHrHn5zdJ-o0Qz1ZYd9P36tE2QIy8cO8c&query="
geolocator = Nominatim(user_agent="myagent")
session = Session()
useragent = 'Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/_BuildID_) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36'
browser = RoboBrowser(user_agent=useragent, session=session, parser='html.parser',)
logging.basicConfig(filename='insert.log',level=logging.DEBUG)
file1 = open("myfile.txt","w")

def convert_si_to_number(x):
    total_stars = 0
    if 'K' in x:
        if len(x) > 1:
            total_stars = float(x.replace('K', '')) * 1000  # convert k to a thousand
    elif 'k' in x:
        if len(x) > 1:
            total_stars = float(x.replace('k', '')) * 1000  # convert k to a thousand
    elif 'M' in x:
        if len(x) > 1:
            total_stars = float(x.replace('M', '')) * 1000000  # convert M to a million
    elif 'B' in x:
        total_stars = float(x.replace('B', '')) * 1000000000  # convert B to a Billion
    else:  # Less than 1000
        try:
            total_stars = int(x)
        except ValueError:  # Catch failture
            pexit('Error: convert_si_to_number('+str(x)+')')
    return int(total_stars)

def login():
    try:
        print('Logging in to facebook...')
        browser.open("https://facebook.com") # Facebook profile's language need to be EN-US!
        login_form = browser.get_form(id='login_form')
        login_form['email'].value = CONFIG.FB_EMAIL
        login_form['pass'].value = CONFIG.FB_PASSWORD
        browser.submit_form(login_form)
        # if ('<form action="https://m.facebook.com/login' in browser.parsed.encode().decode("utf-8")):
        #     pexit('Login failed')
    except Exception as e:
        print(str(e))
        logging.exception("login error"+str(e))
        # logger.exception('This is a logging in error')

    '''with open(file, "w", encoding="utf-8") as text_file:
        print(browser.parsed, file=text_file)
    print('Opening browser...')
    webbrowser.open_new_tab(file)'''

def pexit(printit=''):
    print(printit)
    exit(0)



inserted_count = 0

def getEventJson(tree):
    try:
        s = tree.xpath('//head/script[7]')
        s1 = etree.tostring(s[0]).decode("utf-8")
        x = xml.dom.minidom.parseString(s1)
        y = json.loads(x.getElementsByTagName('script')[0].firstChild.nodeValue)
        return y
    except Exception as e: # Catch failture
        print('\nGetevent error')
        logging.exception("Getevent error"+ str(etree.tostring(tree[0])))
        return {} 


def getevent(eventid, pageid):
    global inserted_count
    try:
        event = query_db("SELECT * FROM events WHERE id=%s"%eventid)
        if len(event) == 0:
            print('\x1b[6;33;40m' + 'Getting event: ' + str(eventid) + '\x1b[0m', end="")
            eventurl = "https://mobile.facebook.com/events/"+eventid
            browser.open(eventurl)

            tree = html.fromstring(browser.parsed.encode())

            # Getting the clear image for the event
            hd_img = gei(eventid)
            if hd_img is not None:
                print(hd_img)
                event_photo = hd_img

            '''with open(file, "w", encoding="utf-8") as text_file:
                print(browser.parsed.encode(), file=text_file)
            print('Opening browser...')
            webbrowser.open_new_tab(file)
            sleep(1)'''
            event_tree = getEventJson(tree)
            if event_tree:
                event_description = ''
                event_title = ''
                event_photo = '' 
                if "description" in event_tree:
                    event_description = event_tree['description'].replace("'", "`")
                if "name" in event_tree:
                    event_title = event_tree['name'].replace("'", "`")
                if "image" in event_tree:
                    if hd_img is None:
                        event_photo = event_tree['image']
                    else:
                        event_photo = hd_img

                dateto = None
                datefrom = None
                event_location = ''
                event_place = ''
                event_ago = ''
                event_going = ''
                event_interested = ''
                if "startDate" in event_tree:
                    datefrom = event_tree['startDate']
                if "endDate" in event_tree:
                    dateto = event_tree['endDate']
                if "location" in event_tree:
                    event_place = event_tree['location']['name']
                    if event_place is not None:
                        event_location += event_tree['location']['name'] + ', '
                    if "address" in event_tree['location']:
                        event_location1 = event_tree['location']['address']['streetAddress']
                        event_location2 = event_tree['location']['address']['postalCode']
                        event_location3 = event_tree['location']['address']['addressLocality']

                        # Cleaning datas
                        event_location1 = event_location1 if event_location1 is not None else ''
                        event_location2 = event_location2 if event_location2 is not None else ''
                        event_location3 = event_location3 if event_location3 is not None else ''

                        event_location += event_location1 + ', ' + event_location2 + ', ' + event_location3
                if "address" in event_tree:
                    event_location1 = event_tree['address']['streetAddress']
                    event_location2 = event_tree['address']['postalCode']
                    event_location3 = event_tree['address']['addressLocality']

                    # Cleaning datas
                    event_location1 = event_location1 if event_location1 is not None else ''
                    event_location2 = event_location2 if event_location2 is not None else ''
                    event_location3 = event_location3 if event_location3 is not None else ''
                    
                    event_location += event_location1 + ', ' + event_location2 + ', ' + event_location3
                if "image" in event_tree:
                    if hd_img is None:
                        event_photo = event_tree['image']
                    else:
                        event_photo = hd_img
                    

                # event_description = get_description(tree)
                # event_ago_location = get_event_ago(tree)
                # event_going_number = get_going(tree)
                # event_title = get_title(tree).replace("'","")
                # event_date_place = get_date_place(tree)
                # event_photo = get_photo(tree)
                '''with open(file, "w", encoding="utf-8") as text_file:
                    print(browser.parsed.encode(), file=text_file)
                print('Opening browser...')
                webbrowser.open_new_tab(file)'''

                '''
                if " dates left" in event_date_place[0]:
                    print(' - \033[1;31;0mError while getting date:\033[1;0;0m')
                    print(event_date_place)
                    dateto = None
                    datefrom = None
                else:
                    splitted = event_date_place[0].split(' – ', 1)
                    if len(splitted) < 2:
                        splitted = event_date_place[0].split(' - ', 1) # – - not equal!!!
                    if len(splitted) < 2:
                        print(' - \033[1;31;0mError while splitting date: \033[1;0;0m' + event_date_place[0])
                        dateto = None
                        datefrom = None
                    else:
                        print(splitted[0])
                        datefrom = timestring.Date(splitted[0]).date
                        dateto = timestring.Date(splitted[0][:-4] + splitted[1]).date
                '''
                '''datefrom = "2018-01-01 01:01:01"
                dateto = "2018-01-01 01:01:01"'''

                '''
                lines = ''
                for line in event_description:
                    line = line.replace("'","")
                    lines += line + '<br>'
                if (len(event_ago_location) == 2):
                    event_ago = event_ago_location[0]
                    event_location = event_ago_location[1]
                elif(len(event_ago_location) == 1):
                    print(' - event_ago is NULL', end='')
                    event_ago = None
                    event_location = event_ago_location[0]
                else:
                    event_ago = None
                    event_location = None
                    print(' - get_event_ago() --> event_ago_location lenght is '+str(len(event_ago_location)), end='')

                if len(event_date_place) != 1:
                    if len(event_date_place) == 2:
                        event_place = [event_date_place[1]]
                    else:
                        with open(file, "w", encoding="utf-8") as text_file:
                            print(browser.parsed.encode(), file=text_file)
                        pexit('event_date_place lenght is not 1: '+str(event_date_place))
                '''
                print('going sele list')
                sele_list = checkTicket(eventid)
                
                event_going = sele_list[0]
                event_interested = sele_list[1]
                #price = 'Free'
                if sele_list[-1]:
                    price = 'Paid'
                else:
                    price = 'Free'

                # Create a new record
                now = datetime.datetime.now()

                #event_date = event_date_place[0]
                #event_place = event_date_place[1]
                #event_going = event_going_number[0]
                #event_interested = event_going_number[1]#

                city = ''
                state = ''
                country = ''
                lat = '0.0'
                lon = '0.0'
                timezone = ''
                try:
                    if event_location is not None:
                        if "," in event_location:
                            cityState = event_location.split(",")[-2:]
                            city = ''.join([i for i in cityState[0] if not i.isdigit()])
                            state = ''.join([i for i in cityState[1] if not i.isdigit()])
                            qs = event_location
                            
                            r = requests.get(mapurl+str(qs))
                            r = r.json()
                            if r['status'] == "OK":
                                country = r['results'][0]['formatted_address'].split(",")[-1::][0].strip()
                                lat = str(r['results'][0]['geometry']['location']['lat'])
                                lon = str(r['results'][0]['geometry']['location']['lng'])
                            if lat == '0.0' and lon =='0.0':
                                qs = event_place
                                r = requests.get(mapurl+str(qs))
                                r = r.json()
                                if r['status'] == "OK":
                                    country = r['results'][0]['formatted_address'].split(",")[-1::][0].strip()
                                    lat = str(r['results'][0]['geometry']['location']['lat'])
                                    lon = str(r['results'][0]['geometry']['location']['lng'])
                    else:
                        qs = event_place
                        r = requests.get(mapurl+str(qs))
                        r = r.json()
                        if r['status'] == "OK":
                            city = r['results'][0]['formatted_address'].split(",")[-2::][0].strip()
                            country = r['results'][0]['formatted_address'].split(",")[-2::][1].strip()
                            lat = str(r['results'][0]['geometry']['location']['lat'])
                            lon = str(r['results'][0]['geometry']['location']['lng'])

                except Exception as e:
                    # logging.exception("Getevent error"+str(e))
                    print('\n\nException occured in the event location place\n\n')
                    logger2.exception(e)
                
                event_date = datefrom
                '''
                try:
                    if event_date is not None:
                        if "from" in event_date:
                            pieces = event_date.split(" from ")
                            new_date_format = str(parse(pieces[0]).date())
                            newpieces = pieces[1].split(" ")
                            timepieces = newpieces[0].split("-")
                            datefrom = new_date_format + ' ' + timepieces[0]+':00'
                            dateto = new_date_format + ' ' + timepieces[1]+':00'
                            timezone = newpieces[1]
                        
                        if "at" in event_date:
                            pieces = event_date.split(" at ")
                            new_date_format = str(parse(pieces[0]).date())
                            newpieces = pieces[1].split(" ")
                            datefrom = new_date_format + ' ' + newpieces[0]+':00'
                            dateto = new_date_format + ' ' + newpieces[0]+':00'
                            timezone = newpieces[1]


                except Exception as e:
                    logging.exception("Getevent error"+str(e))
                '''

                # Cleaning all things that could cause syntax errors
                eventid = replace_syntax(eventid)
                pageid = replace_syntax(pageid)
                event_title = replace_syntax(event_title)
                event_description = replace_syntax(event_description)
                event_date = replace_syntax(event_date)
                datefrom = replace_syntax(datefrom)
                dateto = replace_syntax(dateto)
                event_place = replace_syntax(event_place)
                event_ago = replace_syntax(event_ago)
                event_location = replace_syntax(event_location)
                event_going = replace_syntax(event_going)
                event_interested = replace_syntax(event_interested)
                event_photo = replace_syntax(event_photo)
                lat = replace_syntax(lat)
                lon = replace_syntax(lon)
                now = replace_syntax(now)
                price = replace_syntax(price)
                city = replace_syntax(city)
                state = replace_syntax(state)
                country = replace_syntax(country)
                timezone = replace_syntax(timezone)

                sql = "INSERT INTO events (`id`, `page`, `title`, `description`, `date`, `datefrom`, `dateto`, `place`, `ago`, `location`, `going`, `interested`, `photo`, `lat`, `lon`, `lastupdate`, `price`, `city`, `state`, `country`, `LNG`) VALUES (%s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (eventid, pageid, event_title, event_description, event_date, datefrom, dateto, event_place, event_ago, event_location, event_going, event_interested, event_photo, lat, lon, now, price, city, state, country,timezone)
                # logging.info("SQL->"+str(sql))
                logger.info("SQL->"+str(sql))
                insert_val = upsert_db(sql)
                # print(sql)
                print('\n\nThe insert value', insert_val)
                if insert_val is True:
                    now = datetime.datetime.now()
                    print('\n\nAn information was just inserted\n\n')
                    # logging.info('INFORTATION INSERTED %s' , str(now))
                    logger.info('INFORTATION INSERTED %s' , str(now))
                    inserted_count += 0
                else:
                    logger.warning('INFORMATION NOT INSERTED %s' , str(now))
        
    except Exception as e: # Catch failture
        print('\nGetevent error')
        logger2.exception('\nThis is the ending error, the events crawler has stopped working\n')
        # logging.exception("Getevent error"+str(e))
        pexit()

def get_date_place(tree):
    event_date_place = tree.xpath('//div[@id="event_summary"]/div/div/table/tbody/tr/td[2]/dt/div/text()')  # [0] == date (Friday, November 16, 2018 at 8 PM – 11:55 PM)   [1] == place (Expresszó)
    if (len(event_date_place) == 0):
        pexit('get_date() error. len(event_date_place) == 0')
    if (len(event_date_place) == 1):
        event_date_place = (event_date_place[0], 'NULL')
        print('event_place is NULL')
    return event_date_place


def get_event_ago(tree):
    print(etree.tostring(tree[0])) 
    event_ago_temp = tree.xpath('//div[@id="event_summary"]/div/div/table/tbody/tr/td[2]/dd/div/text()') # [0] == ago (3 days ago)   [1] == location (Brusznyai út 2., Veszprém, 8200)
    if (len(event_ago_temp) == 3):
        event_ago = [event_ago_temp[0]+event_ago_temp[1],event_ago_temp[2]]
    else:
        event_ago = event_ago_temp
    if (len(event_ago) == 0):
        print(' - get_event_ago() == 0')
    return event_ago

def get_going(tree):
    str = tree.xpath('//div[@id="unit_id_703958566405594"]/div/a/div/text()')  # [0] == going (234)        [1] == intrested (2.1K)
    if (len(str) == 0):
        str = tree.xpath('//div[@id="unit_id_703958566405594"]/div/div/div[2]/a/text()')
    if (len(str) == 0):
        print(' - get_going() --> len(str) == 0', end='')
        event_going_number = ['0', '0']
    else:
        try:
            if (str[0] != 'Details') & (str[0] != ''):
                splitted = str[0].split(' ')
            elif (str[1] != 'Details') & (str[1] != ''):
                splitted = str[1].split(' ')
            else:
                splitted = str[2].split(' ')

            if len(splitted) == 1:
                if len(str) == 1:
                    going_str = '0'
                    interest_str = str[0]
                else:
                    going_str = str[0]
                    interest_str = str[1]
            elif len(splitted) < 3:
                print('str: ')
                print(str)
                print(len(splitted))
                print('len(splitted) < 3')
                #pexit('get_goint() error, len(splitted) < 3, == up')
            else:
                going_str = splitted[0]
                interest_str = splitted[3]
        except ValueError:
            print('str: ')
            print(str)
            pexit('get_goint() error, printed below')
        # if (type(going_str) == int) & (type(interest_str) == int):
        #     event_going_number = [going_str, interest_str]
        # else:
        #     event_going_number = [convert_si_to_number(going_str), convert_si_to_number(interest_str)]
        event_going_number = [going_str, interest_str]
    return event_going_number


def get_description(tree):
    #event_description = tree.xpath('//div[@id="unit_id_886302548152152"]/section/text()')
    #event_description = tree.xpath('//AdditionalAttribute[@name="description"]')
    s = tree.xpath('//head/meta[5]')
    s1 = etree.tostring(s[0]).decode("utf-8")
    x = xml.dom.minidom.parseString(s1)
    event_description = x.documentElement.getAttribute("content")
    logging.info('description->'+str(event_description))
    
    if (len(event_description) == 0):
        event_description = ''
    return event_description
    #return ''.join(filter(None, parts))

def get_title(tree):
    event_title = tree.xpath('//h3/text()')  # [0] == date (Friday, November 16, 2018 at 8 PM – 11:55 PM)        [1] == place (Expresszó)
    if (len(event_title) == 0):
        print(event_title)
        pexit(' - get_title() error. len(event_title) == 0')
    return event_title[0]

    

def get_photo(tree):
    src = tree.xpath('//div[@id="event_header"]/a/img/@src')  # src=https://scontent.fbud3-1.fna.fbcdn.net/v/t1.0-9/cp0/e15/q65/c40.0.1119.628/46168765_2003771449645939_8214378811936997376_o.jpg?_nc_cat=1&efg=eyJpIjoiYiJ9&_nc_ht=scontent.fbud3-1.fna&oh=b3bba07c88fd8710a656964bbb322937&oe=5C6BCBEA
    if (len(src) == 0):
        src = tree.xpath('//a[@aria-label="Watch video"]/div/img/@src')  # get video preview image

    if (len(src) == 0):
        print(' - get_photo() error. len(src) == 0', end='')
        return ''
    return src[0]


def getpage(page):
    try:
        print('\x1b[6;32;40m' + 'Getting page: '+page + '\x1b[0m')
        eventurl = "https://mobile.facebook.com/"+page+"?v=events"
        browser.open(eventurl)
        tree = html.fromstring(browser.parsed.encode())
        #print(browser.parsed.encode())
        #strings = tree.xpath('//div[@id="root"]/div/div/div[2]/div/table/tbody/tr/td/div/div/span[3]/div/a[1]/@href')
        strings = tree.xpath('//div[@id="pages_msite_body_contents"]/div/div/div/div[2]/div/div/div/div/div/a[1]/@href')
        #print(str(strings))
        eventids = []
        for string in strings:
            eventids.append(os.path.split(string)[1].split('?')[0])
        istheremore = tree.xpath('//div[@id="m_more_friends_who_like_this"]/a/span/text()')
        while istheremore:
            nexturl = tree.xpath('//div[@id="m_more_friends_who_like_this"]/a/@href')[0]
            browser.open('https://mobile.facebook.com'+nexturl)
            tree = html.fromstring(browser.parsed.encode())
            strings = tree.xpath('//div[@id="root"]/div/div/div[2]/div/table/tbody/tr/td/div/div/span[3]/div/a[1]/@href')
            for string in strings:
                eventids.append(os.path.split(string)[1].split('?')[0])
            istheremore = tree.xpath('//div[@id="m_more_friends_who_like_this"]/a/span/text()')
        try:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = "UPDATE pages SET lastindex = '%s' WHERE page = '%s'" % (now, page)
            logging.info("SQL->"+str(sql))   
            insert_val = upsert_db(sql)
        except Exception as e:
            print('Lastindex update error' + str(now))
            logging.info("Lastindex update error->"+str(e))
        
        return eventids
    except ValueError: # Catch failture
        pexit('Getpage error')

def listpages():
    nowplushour = datetime.datetime.now() + datetime.timedelta(hours=-5)
    sql = "SELECT page FROM pages WHERE datetime(lastindex) < '%s' OR lastindex IS NULL" % (nowplushour)
    pages = []
    for page in query_db(sql):
        pages.append(page[0])
    return pages

def main_job():
    print("Starting Job")
    #login()
    print("Starting list page")
    listpage = listpages()
    # print(listpage)
    #sele_login()
    for pageid in listpage:
        print("getting page"+str(pageid))
        pageevents = getpage(pageid)
        for eventid in pageevents:
            getevent(eventid,pageid)
    nowminday = datetime.datetime.now() + datetime.timedelta(days=-1)
    now = datetime.datetime.now()
    if (inserted_count > 0):
        logger.info(str(now)+'-> '+inserted_count + ' new row inserted')
        # logging.info(str(now)+'-> '+inserted_count + ' new row inserted')
        print(inserted_count + ' new row inserted')
    else:
        logger.info(str(now)+'-> Pages are already updated less than an hour ago, no new events queried')
        # logging.info(str(now)+'-> Pages are already updated less than an hour ago, no new events queried')
        print('Pages are already updated less than an hour ago, no new events queried')
    
    print('Script end at '+str(now.hour)+':'+str(now.minute))
    logger.info('Script end at '+str(now.hour)+':'+str(now.minute))
    # logging.info('Script end at '+str(now.hour)+':'+str(now.minute))


def print_job():
    print('hi')

# @sched.scheduled_job('interval', minutes=1)
# def timed_job():
#     main_job()

# sched.start()

