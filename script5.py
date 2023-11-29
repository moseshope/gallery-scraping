from bs4 import BeautifulSoup
import requests
import sqlite3

#location information is misssed in this website

# Connet to the database 'gallery'
connection = sqlite3.connect('./db/gallery.sqlite')

# Get total count of the images in website
try:
    url = "https://www.nga.gov/bin/ngaweb/collection-search-result/search.pageSize__1.pageNumber__1.lastFacet__artobj_classification.json?sortOrder=DEFAULT&artobj_classification=painting&_=1700427632711"
    res = requests.get(url).json()
    total_cnt = int (res['totalcount'])
except:
    total_cnt = 0

#Fetch image information and insert into DB

url = f"https://www.nga.gov/bin/ngaweb/collection-search-result/search.pageSize__{total_cnt}.pageNumber__1.lastFacet__artobj_classification.json?sortOrder=DEFAULT&artobj_classification=painting&_=1700427632711"
res = requests.get(url).json()
# data = json_loads(res)
results = res['results']

for result in results:
    title = result.get('title', 'Default')
    name = result['artists'][0]['forwardName']
    role = result['artists'][0]['role']
    nation = result['artists'][0]['displaydatecons']
    description = result.get('assistivetext', 'Default')
    artist = f"{name} ({role}) {nation}"
    
    img_url = result.get('imagepath', 'Default')
    date = result.get('displaydate', 'Default')
    style = result.get('classification', 'Default')
    medium = result.get('medium', 'Default')
    dimension = f"{result.get('dimensions1', 'Default')}, {result.get('dimensions2', 'Default')}"
    if title:
        title = title.replace('"', "'")
    if artist:
        artist = artist.replace('"', "'")
    if description:
        description = description.replace('"', "'")
    if img_url:
        img_url = img_url.replace('"', "'")
    if date:
        date = date.replace('"', "'")
    if style:
        style = style.replace('"', "'")
    if medium:
        medium = medium.replace('"', "'")
    if dimension:
        dimension = dimension.replace('"', "'")
    print("------------------------------------------------------------------------------------------------------------------")
    print(f"title: {title}")
    print(f"artist: {artist}")
    print(f"description: {description}")
    print(f"img_url: {img_url}")
    print(f"date: {date}")
    print(f"style: {style}")
    print(f"medium: {medium}")
    print(f"dimension: {dimension}")


    query = f'INSERT INTO gallery_info(title, artist, description, image_url, date, style, medium, dimensions, source) VALUES("{title}", "{artist}", "{description}", "{img_url}", "{date}", "{style}", "{medium}", "{dimension}", "https://www.nga.gov/collection-search-result.html?sortOrder=DEFAULT&artobj_classification=painting&pageSize=30&pageNumber=144&lastFacet=artobj_classification")'
    connection.execute(query)
    connection.commit()

print('Scraping is finished!')