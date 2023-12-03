from bs4 import BeautifulSoup
import requests
import sqlite3
# 14424
# Connet to the database 'gallery'
connection = sqlite3.connect('./db/gallery.sqlite')

# Get total count of the images in website
try:
    url = "https://www.metmuseum.org/mothra/collectionlisting/search?showOnly=withImage&offset=0&material=Paintings&perPage=1"
    res = requests.get(url).json()
    total_cnt = int (res['totalResults'] / 100) + 1
except:
    total_cnt = 0
error_cnt = 0

#Fetch image information and insert into DB
for i in range(0, total_cnt):
    try:
        url = f"https://www.metmuseum.org/mothra/collectionlisting/search?showOnly=withImage&offset={i * 100}&material=Paintings&perPage=100"
        res = requests.get(url).json()
        results = res['results']
        for result in results:
            try:
                title = result.get('title', '')
                artist = result.get('artist', '')
                description = result.get('description', '')
                img_url = result.get('largeImage', '')
                date = result.get('date', '')
                medium = result.get('medium', '')
                location = result.get('galleryInformation', '')
                detail_url = result.get('url', '')
                response = requests.get(detail_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    values = soup.find_all('span', class_={'artwork-tombstone--label'})
                    if soup.find(class_='artwork--not-openaccess'):
                        img_url = f"https://images.metmuseum.org/CRDImages/{img_url}"
                    else:
                        img_url = soup.find(class_='artwork__interaction artwork__interaction--download').find('a').get('href')
                    for value in values:
                        if value.text == "Dimensions:":
                            dimension = value.find_next_sibling('span', class_={'artwork-tombstone--value'}).text
                    if soup.find(attrs={'itemprop': 'description'}):
                        description = soup.find(attrs={'itemprop': 'description'}).text

                if title:
                    title = title.replace("'", '"')
                if artist:
                    artist = artist.replace("'", '"')
                if description:
                    description = description.replace("'", '"')
                if img_url:
                    img_url = img_url.replace("'", '"')
                if date:
                    date = date.replace("'", '"')
                if medium:
                    medium = medium.replace("'", '"')
                if dimension:
                    dimension = dimension.replace("'", '"')
                if location:
                    location = location.replace("'", '"')
                
                print("-----------------------------------------------------------------------------------------------")
                print(f"title: {title}")
                print(f"artist: {artist}")
                print(f"description: {description}")
                print(f"img_url: {img_url}")
                print(f"date: {date}")
                print(f"medium: {medium}")
                print(f"dimension: {dimension}")
                print(f"location: {location}")

                query = f"INSERT INTO gallery_info(title, artist, description, image_url, style, date, medium, location, dimensions, source) VALUES('{title}', '{artist}', '{description}', '{img_url}', 'painting', '{date}', '{medium}', '{location}', '{dimension}', '{detail_url}')"
                connection.execute(query)
                connection.commit()
            except Exception as err:
                print(f"Unexpected => {err=}, {type(err)=}")
                error_cnt += 1
    except Exception as err:
        print(f"Unexpected => {err=}, {type(err)=}")
        error_cnt += 1
print(f'total_error: {error_cnt}')
print('Scraping is finished!')