from bs4 import BeautifulSoup

from .models import Watchlist

import urllib.parse as urlparse
from urllib.parse import parse_qs
import requests
def get_product_info(page_,url_,user=''):
    url = url_
    page=page_

    product_name =''
    price_th =''
    price = 0
    product_pic_url =''
    domain = ''


    slash_list = url.split('/')
    domain = slash_list[2]

    data =urlparse.urlparse(url)
    try:
        pid = parse_qs(data.query)['pid'][0]
    except KeyError:
        pid = 'none'
    # print(pid)
    exists = False
    if pid != 'none':
        try:
            # get data from db for current user and check if pid exists
            p_data = Watchlist.objects.get(user_id=user,pid=pid)
        except :
            pass
        else:
            exists = True

    soup = BeautifulSoup( page.content, 'html.parser')

    name_tag = soup.find(class_='B_NuCI')
    if name_tag:
        product_name = name_tag.get_text()
        # print(product_name)

    price_tag = soup.find(class_='_16Jk6d')
    if price_tag:
        price_th = price_tag.get_text()[1:]
        price = int(price_th.replace(',',''))
        # print(price)

    availability_tag = soup.find(class_='_16FRp0')
    availability = 'In stock'
    if availability_tag:
        availability = availability_tag.get_text()
    # print('availability:',availability)


    picture_tag = soup.find(class_='q6DClP')

    if picture_tag:
        picture_tag_soup = BeautifulSoup(str(picture_tag),'html.parser')
        style_attr = picture_tag_soup.div['style']
        product_pic_url = style_attr[21:-1]
        product_pic_url = product_pic_url.replace('128','400')
        # print(product_pic_url)
    data ={
            'product_url':url,
            'product_name':product_name,
            'availability':availability,
            'price':price,
            'pid':pid,
            'exists':exists,
            'price_th':price_th,
            'domain':domain,
            'product_pic_url':product_pic_url
            }
    return data