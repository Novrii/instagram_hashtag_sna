import time
from selenium import webdriver
import os


options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

driver = webdriver.Chrome(chrome_options=options)
driver.get("https://instagram.com")
time.sleep(3)
driver.quit()
