from bs4 import BeautifulSoup
import requests
import sqlite3
import re
import json

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
                    date = location = description = dimension = img_url = ''
                    img_link = result.find('td', class_='cs-result-image').find('a')
                    if img_link:
                        img_url = img_link.get('href')
                    content = result.find('div', class_='cs-result-data-full').find_all('tr')
                    title = content[0].find('p', class_='cs-record-link').find('strong').text
                    artist = content[1].find('td', class_='cs-value').find('p').text
                    style = content[2].find('td', class_='cs-value').find('p').text
                    medium = content[3].find('td', class_='cs-value').find('p').text
                    detailed_url = content[0].find('p', class_='cs-record-link').find('a').get('href')
                    detail_res = requests.get(detailed_url)
                    if detail_res.status_code == 200:
                        data = BeautifulSoup(detail_res.text, 'html.parser')
                        try:
                            description = json.loads(data.find('script', {'type':'application/ld+json'}).text)['description']
                        except:
                            description = ''
                        try:
                            img_url = json.loads(data.find('script', {'type':'application/ld+json'}).text)['thumbnailUrl']
                            img_url = img_url.replace('!100,100', 'full')
                        except:
                            print(img_url)
                    for datas in content:
                        if datas.find(class_='cs-label').find('p').text == 'Date:':
                            date = datas.find(class_='cs-value').find('p').text
                        if datas.find(class_='cs-label').find('p').text == 'Source:':
                            location = datas.find(class_='cs-value').find('p').text
                        if datas.find(class_='cs-label').find('p').text == 'Dimensions:':
                            dimension = datas.find(class_='cs-value').find('p').text
                    if title:
                        title = title.replace("'", '"')
                    if artist:
                        artist = artist.replace("'", '"')
                    if style:
                        style = style.replace("'", '"')
                    if medium:
                        medium = medium.replace("'", '"')
                    if date:
                        date = date.replace("'", '"')
                    if location:
                        location = location.replace("'", '"')
                    if dimension:
                        dimension = dimension.replace("'", '"')
                    if description:
                        description = description.replace("'", '"')
                    detailed_url = detailed_url.replace("'", '"')

                    print("-----------------------------------------------------------------------------------------------")
                    print(f"title: {title}")
                    print(f"artist: {artist}")
                    print(f"style: {style}")
                    print(f"img_url: {img_url}")
                    print(f"date: {date}")
                    print(f"medium: {medium}")
                    print(f"dimension: {dimension}")
                    print(f"location: {location}")
                    print(f"description: {description}")
                    

                    query = f"INSERT INTO gallery_info(title, artist, description, image_url, style, date, medium, location, dimensions, source) VALUES('{title}', '{artist}', '{description}', '{img_url}', '{style}', '{date}', '{medium}', '{location}', '{dimension}', '{detailed_url}')"
                    connection.execute(query)
                    connection.commit()
                except Exception as err:
                    print('00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
                    print(f"Unexpected => {err=}, {type(err)=}")
                    error_count += 1
                    continue
        else: error_count += 1
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        error_count += 1
        continue
print('Scraping is finished!')