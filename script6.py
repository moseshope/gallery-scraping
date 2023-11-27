from bs4 import BeautifulSoup
import requests
import sqlite3
import re
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Connet to the database 'gallery'
connection = sqlite3.connect('./db/gallery.sqlite')

flag = True
next_param = ""

while flag: 
    url = f"https://artsandculture.google.com/api/objects/partner?s=200&pt={next_param}&hl=en&_reqid=&rt=j"
    response = requests.get(url)
    # time.sleep(0.5)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.text.replace(")]}'", "")
        value = json.loads(data)
        results = value[0][0][2]
        for result in results:
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            try:
                next_url = f"https://artsandculture.google.com{result[4]}"
                driver.get(next_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "jP8Fed")))
                res = driver.page_source
                soup = BeautifulSoup(res, 'html.parser')
                try:
                    view_all_url = f"https://artsandculture.google.com{soup.find(class_='FKo5md').find('a').get('href')}"
                    driver.get(view_all_url)
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "DuHQbc")))
                    all_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    final_links = all_soup.find_all(class_='DuHQbc')
                    for final_link in final_links:
                        driver.get(f"https://artsandculture.google.com{final_link.find('a').get('href')}")
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "DRVwp")))
                        ScrollNumber = 3
                        for i in range(1,ScrollNumber):
                            driver.execute_script("window.scrollTo(1,50000)")
                            time.sleep(1)
                        print("------------------Delay 2s--------------------------")
                        page_source = driver.page_source
                        title = artist = date = dimension = style = medium = img_url = ""
                        final_soup = BeautifulSoup(page_source, 'html.parser')
                        detail_links = final_soup.find_all('a', class_="e0WtYb DRVwp bJyJVb PJLMUc")
                        for detail_link in detail_links:
                            img_url = detail_link.get('data-bgsrc').replace('"', "'")
                            driver.get(f"https://artsandculture.google.com{detail_link.get('href')}")
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "f9CV0")))
                            detail_soup = BeautifulSoup(driver.page_source, 'html.parser')        
                            gallery_datas = detail_soup.find(class_="rw8Th QwmCXd").find(class_="ve9nKb").find_all('li')
                            for gallery_data in gallery_datas:
                                result_data = gallery_data.text
                                if result_data.startswith('Title'):
                                    title = result_data.replace('Title: ', '').replace("'", '"')
                                if result_data.startswith('Creator'):
                                    artist = result_data.replace('Creator: ', '').replace("'", '"')
                                if result_data.startswith('Date Created'):
                                    date = result_data.replace('Date Created: ', '').replace("'", '"')
                                if result_data.startswith('Physical Dimensions'):
                                    dimension = result_data.replace('Physical Dimensions: ', '').replace("'", '"')
                                if result_data.startswith('Type'):
                                    style = result_data.replace('Type: ', '').replace("'", '"')
                                if result_data.startswith('Medium'):
                                    medium = result_data.replace('Medium: ', '').replace("'", '"')
                            print('--------------------------------------------------------------------------------------------------------------------')
                            print(f"title: {title}")
                            print(f"img_url: {img_url}")
                            print(f"artist: {artist}")
                            print(f"date: {date}")
                            print(f"dimension: {dimension}")
                            print(f"style: {style}")
                            print(f"medium: {medium}")
                            query = f"INSERT INTO gallery_info(title, artist, image_url, style, date, medium, dimensions, source) VALUES('{title}', '{artist}', '{img_url}', '{style}', '{date}', '{medium}', '{dimension}', 'https://artsandculture.google.com/partner')"
                            connection.execute(query)
                            connection.commit()
                                
                except Exception as err:
                    print(f"Unexpected => {err=}, {type(err)=}")
            except Exception as err:
                    print(f"Unexpected => {err=}, {type(err)=}")
        try:
            next_param = value[0][0][8]
            print(next_param)
        except Exception as err:
            flag = False
    else:
        print(f"Error 4: {response.status_code}")

driver.quit()

print('Scraping is finished!')