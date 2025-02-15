import datetime
import random
import sys
import time
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


def database_crawler():
    today = datetime.datetime.now()
    print(today)

    print("scheduled job active")
    products = Watchlist.objects.all()
    for product in products:
        user_data = User.objects.get(id=product.user_id)
        time.sleep(
            random.randint(10, 24)
        )  # a random delay before each request so we dont overwhelm the server.
        page = requests.get(url=product.product_url, timeout=10)  # gathering data from server
        product_data_from_server = get_product_info(
            page_=page, url_=product.product_url
        )  # 'product_data_from_server'  will contain a dictionary

        new_price = product_data_from_server.get("price")
        new_price_th = product_data_from_server.get("price_th")
        new_availability = product_data_from_server.get("availability")

        product.price = new_price
        product.price_th = new_price_th
        product.availability = new_availability
        product.save()  # update the newly gathered data to the database.
        print("save to DB ok")

        avilable_bool = new_availability == "In stock"
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
            mailer_obj.save()

        elif avilable_bool and product.availability != "In stock":
            mailer_dict["is_avail"] = True
            mailer_obj = MailingList(**mailer_dict)
            mailer_obj.save()

        elif new_price < product.price:
            mailer_dict["is_price_drop"] = True
            mailer_obj = MailingList(**mailer_dict)
            mailer_obj.save()

        # if end
    # loop end
    mailer()  # call mailer and send mails to users in mailing list
    print("Scheduled run finished")


def mailer():
    print("Mailer service active")
    mailer_obj = MailingList.objects.filter(status="pending")
    for mail in mailer_obj:
        user_id = mail.user_id
        product_id = mail.product_id
        user_obj = User.objects.get(id=user_id)
        product_obj = Watchlist.objects.get(id=product_id)

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
            subject = product_obj.product_name + " is back in stock"
            mail_message_dict["subject"] = subject
            mail_message_dict["msg1"] = (
                "An item in your watchlist is now available with a pricedrop"
            )
            html_message = render_to_string("linkadd/email.html", mail_message_dict)
            message = strip_tags(html_message)
            send_mail(subject, message, email_from, email_to, html_message=html_message)

        elif mail.is_avail:
            # send mail about product availability
            subject = product_obj.product_name + " is back in stock"
            mail_message_dict["subject"] = subject
            mail_message_dict["msg1"] = "An item in your watchlist is back in stock"
            html_message = render_to_string("linkadd/email.html", mail_message_dict)
            message = strip_tags(html_message)
            send_mail(subject, message, email_from, email_to, html_message=html_message)

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
            send_mail(subject, message, email_from, email_to, html_message=html_message)

        mail.status = "sent"
        mail.save()
    # loop end


def start():
    tz = get_localzone()
    print(tz)
    scheduler = BackgroundScheduler({"apscheduler.timezone": tz})
    scheduler.add_jobstore(DjangoJobStore(), "default")
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
