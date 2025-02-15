import urllib.parse as urlparse
from urllib.parse import parse_qs
from bs4 import BeautifulSoup

from django.db.models import Q

from .models import Watchlist


def get_product_info(page_, url_, user="", for_crawling=False, product_id=None):
    if for_crawling:
        print(f"gathering data for {product_id}")

    url = url_
    page = page_

    product_name = ""
    price_th = ""
    price = 0
    product_pic_url = ""
    domain = ""

    slash_list = url.split("/")
    domain = slash_list[2]

    data = urlparse.urlparse(url)
    try:
        pid = parse_qs(data.query)["pid"][0]
    except KeyError:
        pid = "none"
    exists = False
    if pid != "none" or for_crawling:
        _query = Q(pid=pid)
        if user:
            _query &= Q(user=user)
        # get data from db for current user and check if pid exists
        exists = Watchlist.objects.filter(_query).exists()

    soup = BeautifulSoup(page.content, "html.parser")

    name_tag = soup.find(class_="VU-ZEz")
    if name_tag:
        product_name = name_tag.get_text()

    price_tag = soup.find(class_="CxhGGd")
    if price_tag:
        price_th = price_tag.get_text()[1:]
        price = int(price_th.replace(",", ""))

    availability_tag = soup.find(class_="R4PyiO")
    availability = "In stock"
    if availability_tag:
        availability = availability_tag.get_text()

    picture_tag = soup.find(class_="DByuf4")

    if picture_tag:
        picture_tag_soup = BeautifulSoup(str(picture_tag), "html.parser")
        product_pic_url = picture_tag_soup.img.get("src")
    data = {
        "product_url": url,
        "product_name": product_name,
        "availability": availability,
        "price": price,
        "pid": pid,
        "exists": exists,
        "price_th": price_th,
        "domain": domain,
        "product_pic_url": product_pic_url,
        "product_id": product_id,
    }
    return data
