from os import error
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from time import sleep
import re

home_url = 'https://tabelog.com/tokyo/rstLst/?vs=1&sa=%E6%9D%B1%E4%BA%AC%EF%BC%88%E3%81%99%E3%81%B9%E3%81%A6%EF%BC%89&sk=%25E7%2584%25BC%25E8%2582%2589&lid=top_navi1&vac_net=&svd=20211029&svt=1900&svps=2&hfc=1&Cat=RC&LstCat=RC13&LstCatD=RC1301&LstCatSD=RC130101&cat_sk=%E7%84%BC%E8%82%89'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=r'C:\Users\saijo taito\Desktop\bitscript\練習\tabelog\chromedriver.exe',options=options)
driver.implicitly_wait(10)
driver.get(home_url)

url_list = []
for i in range(2):
    url = driver.current_url
    url_list.append(url)
    
    try:
        sleep(3)
        driver.find_element_by_css_selector('a.c-pagination__arrow').click()
    except:
        driver.quit()
        break
print('url_list取得完了')

d_list = []
for i,url in enumerate(url_list):
    print('='*30,i+1,'ページ目','='*30)
    sleep(3)
    res = requests.get(url,timeout=3)
    soup = BeautifulSoup(res.content,'lxml')

    a_tags = soup.select('h3.list-rst__rst-name > a')
    for i,a_tag in enumerate(a_tags):
        print('='*30,i,'='*30)
        page_url = a_tag.get('href')
        sleep(3)
        page_res = requests.get(page_url)
        page_res.raise_for_status()
        page_soup = BeautifulSoup(page_res.content,'lxml')

        shop_name = page_soup.select_one('div.rstinfo-table__name-wrap > span').text
        shop_name = re.sub('\n\t*',' ',shop_name)
        tel = page_soup.select_one('p.rstdtl-side-yoyaku__tel-number').text
        tel = tel.strip()
        mail = ' '
        pref = page_soup.select_one('p.rstinfo-table__address > span:first-of-type > a').text
        address = page_soup.select_one('p.rstinfo-table__address > span:nth-of-type(2)').text
        number = re.search('[0-9].*',address)
        if number:
            number = number.group().replace('-','ー')
        else:
            number = ' '
        city = re.sub(number,' ',address)
        building = page_soup.select_one('p.rstinfo-table__address > span:last-of-type').text

        web_site = page_soup.select_one('p.homepage > a')
        if web_site:
            web_site = web_site.get('href')
            if 'https' in web_site:
                ssl = True
            else:
                ssl = False
        else:
            web_site = ' '
            ssl = ' '
        
        d_list.append({
            '店舗名':shop_name,
            '電話番号':tel,
            'メールアドレス':mail,
            '都道府県':pref,
            '市町村区':city,
            '番地':number,
            '建物名':building,
            'HPのURL':web_site,
            'SSL証明書':ssl
        })

df = pd.DataFrame(d_list)
df.to_csv('shop_list2.csv',index=None,encoding='utf-8-sig')