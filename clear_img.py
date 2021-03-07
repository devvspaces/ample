from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import CONFIG


def get_event_image(url):
    # try:
    cl='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 a8c37x1j p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl l9j0dhe7 abiwlrkh p8dawk7l'

    # Login facebook with selenium webdriver
    driver = webdriver.Chrome()
    driver.get('http://www.facebook.com')

    username = driver.find_element_by_id('email')
    username.send_keys(CONFIG.FB_EMAIL)
    sleep(0.5)

    password = driver.find_element_by_id('pass')
    password.send_keys(CONFIG.FB_PASSWORD)
    sleep(0.5)

    sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
    sign_in_button.click()
    sleep(0.5)


    # Scrape events page
    print('Scraping link started')
    driver.get(url)
    sleep(5)
    print('Scrape complete')

    # Get photo link
    link=driver.find_element_by_css_selector('a.'+'.'.join(cl.split(' ')))
    url_l=link.get_attribute('href')

    # Go to photo page
    driver.get(url_l)
    sleep(5)

    # Get the real image link
    imgs = driver.find_element_by_xpath('//*[@data-visualcompletion="media-vc-image"]')
    src_value = imgs.get_attribute('src')
    # except:
    #     return ''

    return src_value