from bs4 import BeautifulSoup
import requests
import sqlite3

# Connet to the database 'gallery'
connection = sqlite3.connect('./db/gallery.sqlite')

# Get total count of the images in website
try:
    url = "https://www.metmuseum.org/mothra/collectionlisting/search?showOnly=withImage&offset=0&material=Paintings&perPage=1"
    res = requests.get(url).json()
    total_cnt = int (res['totalResults'] / 100) + 1
except:
    total_cnt = 0

#Fetch image information and insert into DB
for i in range(0, total_cnt):
    try:
        url = f"https://www.metmuseum.org/mothra/collectionlisting/search?showOnly=withImage&offset={i * 100}&material=Paintings&perPage=100"
        res = requests.get(url).json()
        results = res['results']
        for result in results:
            title = result.get('title', 'Default')
            artist = result.get('artist', 'Default')
            description = result.get('description', 'Default')
            img_url = result.get('largeImage', 'Default')
            date = result.get('date', 'Default')
            medium = result.get('medium', 'Default')
            location = result.get('galleryInformation', 'Default')
            detail_url = result.get('url', 'Default')
            response = requests.get(detail_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                values = soup.find_all('span', class_={'artwork-tombstone--label'})
                for value in values:
                    if value.text == "Dimensions:":
                        demension = value.find_next_sibling('span', class_={'artwork-tombstone--value'}).text

            # style = result.get('style', 'Default')
            # genre = result.get('genre', 'Default')
        query = f"INSERT INTO gallery_info(title, artist, description, image_url, date, medium, location, demensions, source) VALUES('{title}', '{artist}', '{description}', '{img_url}', '{date}', '{medium}', '{location}', '{demension}', 'https://www.metmuseum.org/art/collection/search?showOnly=withImage&offset=160&material=Paintings')"
        connection.execute(query)
        connection.commit()
    except:
        continue

print('Scraping is finished!')