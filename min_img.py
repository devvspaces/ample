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


driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=option)

def gei(url):
    print('Scraping link started')
    driver.get(url)
    sleep(5)
    print('Scrape complete')


    link=driver.find_element_by_xpath("//a[@rel='theater']")
    
    
    link.click()
    print('Getting image')
    sleep(10)
    print('Complete')


    # Getting the image now
    img=driver.find_element_by_xpath("//img[@class='spotlight']")
    return img.get_attribute('src')