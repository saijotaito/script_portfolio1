import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import re

base_url = 'https://tabelog.com/rstLst/yakiniku/{}/?sk=%E7%84%BC%E8%82%89&svd=20211025&svt=1900&svps=2'
d_list = []
for i in range(1,2):
    url = base_url.format(i)
    sleep(3)
    res = requests.get(url,timeout=3)
    res.raise_for_status()
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
            number = number.group()
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
df.to_csv('shop_list.csv',index=None,encoding='utf-8-sig')


