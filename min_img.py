import logging

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup




# Create the logger and set the logging level
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


# Create formatter
formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")


# Create file handler
file_handler = logging.FileHandler('hd_img.log')
# Add formatter to the file handler
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)



option = webdriver.ChromeOptions()
#option.binary_location = GOOGLE_CHROME_BIN
option.add_argument("--headless")  
option.add_argument("--disable-dev-shm-usage")
option.add_argument("--no-sandbox")
option.add_argument("--disable-setuid-sandbox")
option.add_argument('--disable-gpu')
option.add_argument("--incognito")


# driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=option)
# driver = webdriver.Chrome('/Users/HP6460B/Downloads/driver_all/chromedriver')

fb_link = 'https://web.facebook.com'

def gei(eventid):
    try:
        url = f'{fb_link}/events/{eventid}' 
        print('Scraping link started ', url)
        driver.get(url)
        sleep(10)
        print('Scrape complete')

        soup = BeautifulSoup(driver.page_source, 'lxml')

        a_el = soup.find('a',attrs={"rel" : "theater"})
        rel_link = fb_link + a_el.attrs.get('href')

        print('Scraping the real link ', rel_link)
        driver.get(rel_link)
        sleep(10)
        print('Scraping complete')


        soup = BeautifulSoup(driver.page_source, 'lxml')
        # print(soup.prettify())

        # data-visualcompletion="media-vc-image"
        img_el = soup.find('img',attrs={"data-visualcompletion" : "media-vc-image"})
        # for img in soup.find_all('img'):
        #     print(img)
        # print(img_el, img_el.attrs.get('src'))


        src_link = img_el.attrs.get('src')
        if src_link:
            print('Found Image')
    except Exception as e:
        print(e)
        logger.exception('Error in the hd image crawler')
        return None
    
    return src_link


    # link=driver.find_element_by_xpath("//div[@id='event_header_primary']").find_element_by_xpath('//a')
    
    # print('Found the link\n\n', link.get_attribute('href'))
    
    
    # link.click()
    # print('Getting image')
    # sleep(10)
    # print('Complete')


    # # Getting the image now
    # img=driver.find_element_by_xpath("//img[@class='spotlight']")
    # return str(img.get_attribute('src'))