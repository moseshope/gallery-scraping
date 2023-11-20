from bs4 import BeautifulSoup
import requests
import sqlite3
import re

#location information is missed in this website

# Connet to the database 'gallery'
connection = sqlite3.connect('./db/gallery.sqlite')

# Get total count of the images in website
try:
    url = "https://www.rijksmuseum.nl/en/search?f=1&p=1&ps=1&type=painting&st=Objects&ii=0"
    res = requests.get(url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        value = soup.find('a', class_={'search-view-button button-like button-big bg-lighter mobile-lg-1-2 button-selected'}).text
        match = re.search(r'(\d{1,3}(?:,\d{3})*\d*)', value)
        if match:
            total_cnt = int(int(match.group(1).replace(',', '')) / 120) + 1
        else:
            total_cnt = 0
except:
    total_cnt = 0

#Fetch image information and insert into DB
for i in range(1, total_cnt + 1):
    try:
        url = f"https://www.rijksmuseum.nl/en/search?f=1&p={i}&ps=12&type=painting&st=Objects&ii=0"
        res = requests.get(url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            results = soup.find_all('figure', class_='brick')
            for result in results:
                img_url = result.find('img').get('data-src')
                title = result.find('figcaption').find('h2', class_='margin-bottom-halfx h3-like').find('a').text
                detail_url = f"https://www.rijksmuseum.nl{result.find('figcaption').find('h2', class_='margin-bottom-halfx h3-like').find('a').get('href')}"
                response = requests.get(detail_url)
                if response.status_code == 200:
                    detail_page = BeautifulSoup(response.text, 'html.parser')
                    identifications = detail_page.find_all('article', class_='group div-loop div-thin div-bottom-none')[0].find('div', class_='group-data').find_all(class_='item-data')
                    style = identifications[1].find('a').text
                    description = identifications[len(identifications) - 1].text
                    artist = detail_page.find_all('article', class_='group div-loop div-thin div-bottom-none')[1].find('div', class_='group-data').find_all(class_='item-data')[0].find('a').text
                    date = detail_page.find_all('article', class_='group div-loop div-thin div-bottom-none')[1].find('div', class_='group-data').find_all(class_='item-data')[1].text
                    materials = detail_page.find_all('article', class_='group div-loop div-thin div-bottom-none')[2].find('div', class_='group-data').find_all(class_='item-data')
                    medium = detail_page.find_all('article', class_='group div-loop div-thin div-bottom-none')[2].find('div', class_='group-data').find_all(class_='item-data')[len(materials) - 2].text
                    demension = detail_page.find_all('article', class_='group div-loop div-thin div-bottom-none')[2].find('div', class_='group-data').find_all(class_='item-data')[len(materials) - 1].text
                    query = f"INSERT INTO gallery_info(title, artist, description, image_url, style, date, medium, demensions, source) VALUES('{title}', '{artist}', '{description}', '{img_url}', '{style}', '{date}', '{medium}', '{demension}', 'https://www.rijksmuseum.nl/en/search?f=1&p=2&ps=12&type=painting&st=Objects&ii=0')"
                    connection.execute(query)
                    connection.commit()
    except:
        continue
print('Scraping is finished!')