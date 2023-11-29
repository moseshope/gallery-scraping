from bs4 import BeautifulSoup
import requests
import sqlite3
import re
# 4819
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
error_count = 0
index = 0
#Fetch image information and insert into DB
for i in range(1, total_cnt + 1):
    print('----1----', i)
    try:
        url = f"https://www.rijksmuseum.nl/en/search?f=1&p={i}&ps=120&type=painting&st=Objects&ii=0"
        res = requests.get(url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            results = soup.find_all('figure', class_='brick')
            for result in results:
                index += 1
                print('----2----', index)
                img_url = result.find('img').get('data-src')
                detail_url = f"https://www.rijksmuseum.nl{result.find('figcaption').find('h2', class_='margin-bottom-halfx h3-like').find('a').get('href')}"
                source = detail_url
                response = requests.get(detail_url)
                if response.status_code == 200:
                    try:                      
                        detail_page = BeautifulSoup(response.text, 'html.parser')
                        title = detail_page.find('h1', class_='h3-like').text
                        artist = title.split(',')[len(title.split(',')) - 2].strip()
                        date = title.split(',')[len(title.split(',')) - 1].strip()
                        medium = detail_page.find('h1', class_='h3-like').find_next_sibling('p').text.split(',')[0].strip()
                        style= 'painting'
                        description = ''
                        if 'More details' in detail_page.find(class_='caption text-subtle').text:
                            identifications = detail_page.find_all('article', class_='group div-loop div-thin div-bottom-none')[0].find('div', class_='group-data').find_all(class_='item-data')
                            description = identifications[len(identifications) - 1].text.strip()
                            dimension = detail_page.find('h1', class_='h3-like').find_next_sibling('p').text.split(',')[1].replace(' More details', '').strip()
                        else :
                            dimension = detail_page.find('h1', class_='h3-like').find_next_sibling('p').text.split(',')[1].replace(' Catalogue entry', '').strip()
                            entry_url = f"https://www.rijksmuseum.nl{detail_page.find(class_='caption text-subtle').find('a').get('href')}"
                            source = entry_url
                            entry_res = requests.get(entry_url)
                            if entry_res.status_code == 200:
                                entry_page = BeautifulSoup(entry_res.text, 'html.parser')
                                description = entry_page.find('article', class_='chapter chapter-entry reset-padding-bottom').text
                                description = description.replace('Entry', '').strip()
                            else:
                                continue
                        if description:
                            description = description.replace("'", '"')
                        if title:
                            title = title.replace("'", '"').strip()
                        if artist:
                            artist = artist.replace("'", '"')
                        if style:
                            style = style.replace("'", '"')
                        if medium:    
                            medium = medium.replace("'", '"')
                        if date:
                            date = date.replace("'", '"')
                        if dimension:
                            dimension = dimension.replace("'", '"')
                        if img_url:
                            img_url = img_url.replace("'", '"')
                            img_url += '0'

                        query = f"INSERT INTO gallery_info(title, artist, description, image_url, style, date, medium, dimensions, source) VALUES('{title}', '{artist}', '{description}', '{img_url}', '{style}', '{date}', '{medium}', '{dimension}', '{detail_url}')"
                        connection.execute(query)
                        connection.commit()
                        print(f"title: {title}")
                        print(f"artist: {artist}")
                        print(f"medium: {medium}")
                        print(f"date: {date}")
                        print(f"dimension: {dimension}")
                        print(f"img_url: {img_url}")
                        print(f"decription: {description}")
                    except Exception as err:
                        print(f"Unexpected => {err=}, {type(err)=}")
                        error_count += 1
                        continue
                else:
                    error_count += 1
        else:
            error_count += 1
    except:
        error_count += 1
        continue
print('Scraping is finished!')