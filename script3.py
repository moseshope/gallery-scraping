from bs4 import BeautifulSoup
import requests
import sqlite3
import re

# Connet to the database 'gallery'
connection = sqlite3.connect('./db/gallery.sqlite')

# Get total count of the images in website
try:
    url = "https://search.getty.edu/gateway/search?q&cat=type&rows=10&srt=a&dir=s&dsp=0&img=0&f=%22Paintings%22&types=%22Paintings%22&pg=1"
    res = requests.get(url, verify=False)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        value = soup.find('strong', id={'cs-results-count'})
        javascript_code = value.find('script').text
        match = re.search(r'\((\d+)\)', javascript_code)
        if match:
            total_cnt = int(int(match.group(1)) / 10) + 1
        else:
            total_cnt = 0
except:
    total_cnt = 0
error_count = 0
#Fetch image information and insert into DB
for i in range(1, total_cnt + 1):
    print("Indexing.... ", i)
    try:
        url = f"https://search.getty.edu/gateway/search?q&cat=type&rows=10&srt=a&dir=s&dsp=0&img=0&f=%22Paintings%22&types=%22Paintings%22&pg={i}"
        res = requests.get(url, verify=False)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            results = soup.find_all('div', class_='cs-result-item')
            for result in results:
                try:
                    img_link = result.find('td', class_='cs-result-image')
                    img_url = img_link.find('img').get('src')
                    content = result.find('div', class_='cs-result-data-full').find_all('tr')
                    title = content[0].find('p', class_='cs-record-link').find('strong').text
                    artist = content[1].find('td', class_='cs-value').find('p').text
                    style = content[2].find('td', class_='cs-value').find('p').text
                    medium = content[3].find('td', class_='cs-value').find('p').text
                    date = content[4].find('td', class_='cs-value').find('p').text
                    location = content[5].find('td', class_='cs-value').find('p').text
                    dimension = content[8].find('td', class_='cs-value').find('p').text
                    title = title.replace("'", '"')
                    artist = artist.replace("'", '"')
                    style = style.replace("'", '"')
                    medium = medium.replace("'", '"')
                    date = date.replace("'", '"')
                    location = location.replace("'", '"')
                    dimension = dimension.replace("'", '"')

                    print("-----------------------------------------------------------------------------------------------")
                    print(f"title: {title}")
                    print(f"artist: {artist}")
                    print(f"style: {style}")
                    print(f"img_url: {img_url}")
                    print(f"date: {date}")
                    print(f"medium: {medium}")
                    print(f"dimension: {dimension}")
                    print(f"location: {location}")

                    query = f"INSERT INTO gallery_info(title, artist, image_url, style, date, medium, location, dimensions, source) VALUES('{title}', '{artist}', '{img_url}', '{style}', '{date}', '{medium}', '{location}', '{dimension}', 'https://search.getty.edu/gateway/search?q&cat=type&rows=10&srt=a&dir=s&dsp=0&img=0&f=%22Paintings%22&types=%22Paintings%22&pg=1')"
                    connection.execute(query)
                    connection.commit()
                except Exception as err:
                    print(f"Unexpected => {err=}, {type(err)=}")
                    error_count += 1
                    continue
        else: error_count += 1
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        error_count += 1
        continue
print('Scraping is finished!')