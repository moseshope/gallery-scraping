from bs4 import BeautifulSoup
import requests
import sqlite3
import re

# Connet to the database 'gallery'
connection = sqlite3.connect('./db/gallery.sqlite')
cnt = 0
error_cnt = 0

def get_gallery_info(contents):
    global error_cnt, cnt
    if not contents.find('div', id='mw-pages'):
        try:
            sub_urls = contents.find_all('div', class_='mw-content-ltr')[1].find_all('a')
            for sub_url in sub_urls:
                sub_result = requests.get(f"https://en.wikipedia.org{sub_url.get('href')}")
                if sub_result.status_code == 200:
                    get_gallery_info(BeautifulSoup(sub_result.text, 'html.parser'))
        except:
            error_cnt += 1
            return
    else:
        if contents.find('div', class_='mw-category mw-category-columns'):
            detail_urls = contents.find('div', class_='mw-category mw-category-columns').find_all('a')
            for detail_url in detail_urls:
                result = requests.get(f"https://en.wikipedia.org{detail_url.get('href')}")
                source = f"https://en.wikipedia.org{detail_url.get('href')}"
                if result.status_code == 200:
                    soup_result = BeautifulSoup(result.text, 'html.parser')
                    title = detail_url.get('title')
                    description = ''
                    if soup_result.find('div', id='mw-content-text').find('p'):
                        description = soup_result.find('div', id='mw-content-text').find('p').text
                        description = description.replace('"', "'")
                    if soup_result.find('table', class_='infobox vevent'):
                        data_table = soup_result.find('table', class_='infobox vevent')
                    else :
                        data_table = []
                    img_url = artist = date = medium = dimension = location = 'NONE'
                    if len(data_table):
                        try:
                            datas =  data_table.find_all('tr')
                            for data in datas:
                                data_value = data.text
                                if data.find('td', class_='infobox-image'):
                                    img_url = data.find('td', class_='infobox-image').find('img').get('srcset').split('//')[2].replace(' 2x', "")
                                if data_value.startswith('Artist'):
                                    artist = data.find(class_='infobox-data attendee').text
                                if data_value.startswith('Year'):
                                    date = data.find('td').text
                                if data.find(class_='infobox-data category'):
                                    medium = data.find(class_='infobox-data category').text
                                if data_value.startswith('Dimensions'):
                                    dimension = data.find('td').text
                                if data_value.startswith('Location'):
                                    location = data.find('td').text
                        except:
                            error_cnt += 1
                            continue
                    else:
                        try:
                            last_result = requests.get(f"https://en.wikipedia.org/{soup_result.find('div', id='mw-content-text').find('figure').find('a').get('href')}")
                            img_url = soup_result.find('div', id='mw-content-text').find('figure').find('a').find('img').get('srcset').split('//')[2].replace(' 2x', "")
                            
                            if last_result.status_code == 200:
                                detailed_soup = BeautifulSoup(last_result.text, 'html.parser')
                                data_table = detailed_soup.find('div', id='shared-image-desc').find('table')
                                description = data_table.find(class_='description').text
                                date = data_table.find(id='fileinfotpl_date').find_next_sibling('td').text
                                medium = data_table.find(id='fileinfotpl_art_medium').find_next_sibling('td').text
                                dimension = data_table.find(id='fileinfotpl_art_dimensions').find_next_sibling('td').text
                                print(detailed_soup.find_all(id='creator'))
                                artist = detailed_soup.find_all(id='creator')[0].text
                                location = detailed_soup.find_all(id='creator')[1].text
                        except:
                            error_cnt += 1
                            continue
                    style = 'painting'
                    if img_url:
                        img_url = f"https://{img_url}"
                        img_url = img_url.replace('"', "'")
                    if artist:
                        artist = artist.replace('"', "'")
                    if location:
                        location = location.replace('"', "'")
                    if description:
                        description = description.replace('"', "'")
                    if date:
                        date = date.replace('"', "'")
                    if medium:
                        medium = medium.replace('"', "'")
                    if dimension:
                        dimension = dimension.replace('"', "'")
                    if title:
                        title = title.replace('"', "'")
                    query = f'INSERT INTO gallery_info(title, description, artist, image_url, style, date, medium, location, dimensions, source) VALUES("{title}", "{description}", "{artist}", "{img_url}", "{style}", "{date}", "{medium}", "{location}", "{dimension}", "{source}")'
                    connection.execute(query)
                    connection.commit()
                    cnt += 1
        return


url = "https://en.wikipedia.org/wiki/Category:Paintings_by_artist"
res = requests.get(url)
if res.status_code == 200:
    soup = BeautifulSoup(res.text, 'html.parser')

#Fetch image information and insert into DB
while 1:
    category_groups = soup.find_all('div', class_='mw-category-group')
    for category_group in category_groups:
        html_contents = category_group.find_all('div', class_='CategoryTreeSection')
        for html_content in html_contents:
            new_link = f"https://en.wikipedia.org{html_content.find('div', class_='CategoryTreeItem').find('a').get('href')}"
            new_res = requests.get(new_link)
            if new_res.status_code == 200:
                new_soup = BeautifulSoup(new_res.text, 'html.parser')
                get_gallery_info(new_soup)
                # break
        # break
    if soup.find('div', id='mw-subcategories').find('a'):
        next_urls = soup.find('div', id='mw-subcategories').find_all('a')
        if next_urls[0].text == 'previous page' and next_urls[1].text == 'next page':
            next_url = f"https://en.wikipedia.org{next_urls[1].get('href')}"
        elif next_urls[0].text == 'next page':
            next_url = f"https://en.wikipedia.org{next_urls[0].get('href')}"
        else:
            break
        next_res = requests.get(next_url)
        if next_res.status_code == 200:
            soup = BeautifulSoup(next_res.text, 'html.parser')
    else:
        break

print('Scraping is finished!')