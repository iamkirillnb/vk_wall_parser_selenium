import os
import zipfile
from selenium import webdriver
from time import sleep
from datetime import date
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import re

my_log = input('Введите логин: ')
my_pass = input('Введите пароль: ')
news_count = int(input('Введите количество новостей: '))

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")

driver = webdriver.Chrome(options=chrome_options)


driver.get("https://vk.com")

username = driver.find_element_by_id("index_email")
password = driver.find_element_by_id("index_pass")

username.send_keys(my_log)
password.send_keys(my_pass)

driver.find_element_by_id("index_login_button").click()

sleep(2)

all_news = []
while len(set(all_news)) <= news_count:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)
    content = driver.find_elements_by_class_name('_post_content')
    for i in content:
        try:
            post_author = i.find_element_by_class_name('post_author').text
            all_news.append(i)
        except NoSuchElementException:
            continue
data_to_exel = {}
img_cnt = 1
img_dict = {}
all_news = list(set(all_news))
for i in all_news[:news_count]:
    data = date.today()
    year, month, day = data.year, data.month, data.day
    post_author = i.find_element_by_class_name('post_author').text

    try:
        share_count = i.find_element_by_css_selector('a.like_btn.share._share').text
    except NoSuchElementException:
        share_count = ''
    try:
        like_count = i.find_element_by_css_selector('a.like_btn.like._like').text
    except NoSuchElementException:
        like_count = ''
    try:
        post_text = i.find_element_by_class_name("wall_post_text").text
    except NoSuchElementException:
        post_text = ''
    if 'вчера' in i.text:
        day -= 1
    post_data = f'{day}.{month}.{year}'
    try:
        count_views = i.find_element_by_class_name("like_views").text
    except NoSuchElementException:
        count_views = ''
    try:
        image = i.find_element_by_class_name('page_post_thumb_wrap').get_attribute('style')
        img_url = re.search(r'(https?://.*.jpg)', image).group()
        img_dict[img_cnt] = img_url
        img_cnt += 1
    except NoSuchElementException:
        image = 'no'
        img_cnt += 1


    data_to_exel.setdefault('name', []).append(post_author)
    data_to_exel.setdefault('data', []).append(post_data)
    data_to_exel.setdefault('context', []).append(post_text)
    data_to_exel.setdefault('likes', []).append(like_count)
    data_to_exel.setdefault('shares', []).append(share_count)
    data_to_exel.setdefault('views', []).append(count_views)


for i, j in img_dict.items():
    driver.get(j)
    img_name = f'{i+1}.png'
    driver.save_screenshot(img_name)
    sleep(1)
    with zipfile.ZipFile('vk_images.zip', 'a') as myzip:
        myzip.write(img_name)
    os.remove(img_name)

df = pd.DataFrame(data_to_exel)
df.to_excel('vk_parser.xlsx', index=False)

driver.close()