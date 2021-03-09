from bs4 import BeautifulSoup
from requests import Session
from robobrowser import RoboBrowser
import lxml


session = Session()
useragent = 'Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/_BuildID_) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36'
browser = RoboBrowser(user_agent=useragent, session=session, parser='html.parser', history=True)

def get_page(link):
    browser.open(link)
    return browser.parsed.decode()

def gei(id):
    fb_link = 'https://web.facebook.com'
    url = fb_link+'/events/'+str(id)

    page_source = get_page(url)
    soup = BeautifulSoup(page_source, 'lxml')
    results = soup.findAll("a")
    first_link = ''
    for i in results:
        href = i.attrs.get('href')
        if href and href.find('photos') != -1:
            if href.find('gm.') != -1:
                first_link = href
                break


    if first_link:
        page_source = get_page(fb_link+first_link)
        # print()
        soup = BeautifulSoup(page_source, 'lxml')
        results = soup.findAll("img", {"data-sigil":"photo-image"})
        for i in results:
            src = i.attrs.get('src').replace('&amp;','&')
            break

    return src