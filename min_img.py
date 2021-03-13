from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

option = webdriver.ChromeOptions()
#option.binary_location = GOOGLE_CHROME_BIN
option.add_argument("--headless")  
option.add_argument("--disable-dev-shm-usage")
option.add_argument("--no-sandbox")
option.add_argument("--disable-setuid-sandbox")
option.add_argument('--disable-gpu')
option.add_argument("--incognito")


# driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=option)
driver = webdriver.Chrome('/Users/HP6460B/Downloads/driver_all/chromedriver')

def gei(url):
    print('Scraping link started')
    driver.get(url)
    sleep(5)
    print('Scrape complete')


    link=driver.find_element_by_xpath("//div[@id='event_header_primary']").find_element_by_xpath('//a')
    
    print('Found the link\n\n', link)
    
    
    link.click()
    print('Getting image')
    sleep(10)
    print('Complete')


    # Getting the image now
    img=driver.find_element_by_xpath("//img[@class='spotlight']")
    return str(img.get_attribute('src'))

url = 'https://web.facebook.com/events/172698764285893'
print(gei(url))