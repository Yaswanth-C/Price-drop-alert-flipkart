import datetime
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from tzlocal import get_localzone

from linkadd.models import MailingList, Watchlist, User
from ..functions import get_product_info


MAX_THREADS = 6

def get_product_data(product, timeout=10):
    """
    This function is used to get the product data from the product URL.
    """
    page = requests.get(url=product.product_url, timeout=timeout)
    return get_product_info(page_=page, url_=product.product_url, for_crawling=True, product_id=product.id)

def database_crawler():
    """
    Crawl the database and get the product data from the product URL.
    """

    today = datetime.datetime.now()
    print(today)

    start = time.perf_counter()
    print("scheduled job active")
    products = Watchlist.objects.in_bulk()

    futures = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for product in products.values():
            user_data = User.objects.get(id=product.user_id)
            futures.append(executor.submit(get_product_data, product=product))

        mailing_objects = []
        for future in as_completed(futures):
            product_data_from_server = future.result()
            product = products.get(product_data_from_server.get("product_id"))
            new_price = product_data_from_server.get("price")
            new_price_th = product_data_from_server.get("price_th")
            new_availability = product_data_from_server.get("availability")

            product.price = new_price
            product.price_th = new_price_th
            product.availability = new_availability
            product.save()  # update the newly gathered data to the database.
            print("save to DB ok")

            avilable_bool = new_availability == "In stock" or "hurry" in new_availability.lower()
            mailer_dict = {
                "user": user_data,
                "product": product,
                "price": new_price,
                "price_th": new_price_th,
            }

            if (avilable_bool and product.availability != "In stock") and (
                new_price < product.price
            ):
                mailer_dict["is_price_drop_and_avail"] = True
                mailer_obj = MailingList(**mailer_dict)
                mailing_objects.append(mailer_obj)

            elif avilable_bool and product.availability != "In stock":
                mailer_dict["is_avail"] = True
                mailer_obj = MailingList(**mailer_dict)
                mailing_objects.append(mailer_obj)

            elif new_price < product.price:
                mailer_dict["is_price_drop"] = True
                mailer_obj = MailingList(**mailer_dict)
                mailing_objects.append(mailer_obj)
            # if end
        MailingList.objects.bulk_create(mailing_objects)
        # loop end
    mailer()  # call mailer and send mails to users in mailing list
    print("Scheduled run finished")
    end = time.perf_counter() - start
    print(f"Finished in {end} seconds")


def _send_email(mailing_object, subject, message, email_from, email_to, html_message):
    """
    Send email to the user.
    """
    send_mail(subject, message, email_from, email_to, html_message=html_message)
    mailing_object.status = "sent"
    mailing_object.save()

def mailer():
    """
    Send email about the product availability and price drop to the users.
    """
    print("Mailer service active")
    mailing_list = MailingList.objects.filter(status="pending").select_related("product", "user")

    futures = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # since sending mail is an IO bound operation, we can use threads to send mails to users
        for mail in mailing_list:
            user_obj = mail.user
            product_obj = mail.product

            subject = ""
            message = ""
            email_from = settings.EMAIL_HOST_USER
            email_to = [
                user_obj.email,
            ]
            mail_message_dict = {
                "subject": "",
                "username": user_obj.username,
                "msg1": "",
                "prod_name": product_obj.product_name,
                "price_new": str(mail.price_th),
                "lastcheck": datetime.datetime.now(),
                "prod_url": product_obj.product_url,
            }

            if mail.is_price_drop_and_avail:
                subject = product_obj.product_name[:70] + " is back in stock at a lower price"
                mail_message_dict["subject"] = subject
                mail_message_dict["msg1"] = (
                    "An item in your watchlist is now available with a price drop"
                )
                html_message = render_to_string("linkadd/email.html", mail_message_dict)
                message = strip_tags(html_message)
                # send_mail(subject, message, email_from, email_to, html_message=html_message)
                futures.append(executor.submit(_send_email, mail, subject, message, email_from, email_to, html_message))

            elif mail.is_avail:
                # send mail about product availability
                subject = product_obj.product_name + " is back in stock"
                mail_message_dict["subject"] = subject
                mail_message_dict["msg1"] = "An item in your watchlist is back in stock"
                html_message = render_to_string("linkadd/email.html", mail_message_dict)
                message = strip_tags(html_message)
                # send_mail(subject, message, email_from, email_to, html_message=html_message)
                futures.append(executor.submit(_send_email, mail, subject, message, email_from, email_to, html_message))

            elif mail.is_price_drop:
                subject = (
                    "[Price Drop]-"
                    + product_obj.product_name
                    + ". Is now at "
                    + str(mail.price_th)
                )
                mail_message_dict["subject"] = subject
                mail_message_dict["msg1"] = "An item in your watchlist is at a lowest price"
                html_message = render_to_string("linkadd/email.html", mail_message_dict)
                message = strip_tags(html_message)
                # send_mail(subject, message, email_from, email_to, html_message=html_message)
                futures.append(executor.submit(_send_email, mail, subject, message, email_from, email_to, html_message))
        # loop end
    for future in as_completed(futures):
        future.result()
    print("Mailer service finished")


def start():
    tz = get_localzone()
    print(tz)
    scheduler = BackgroundScheduler({"apscheduler.timezone": tz})
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # remove all jobs from the scheduler, when starting up.
    scheduler.remove_all_jobs()
    # run this job every 5 hours .....  change the hours=5  to  minutes=5 to run the scheduler every 5 minutes
    scheduler.add_job(
        database_crawler,
        "interval",
        minutes=1,
        name="DB crawling and mailer",
        jobstore="default",
    )

    register_events(scheduler)
    scheduler.start()
    scheduler.print_jobs()
    print("Scheduler started...", file=sys.stdout)
