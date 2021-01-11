from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution

from django.conf import settings
from django.core.mail import send_mail

import sys,datetime,time
from tzlocal import get_localzone
import requests

from linkadd.models import MailingList, Watchlist,User
from ..functions import get_product_info




# This is the function you want to schedule - add as many as you want and then register them in the start() function below
def database_crawler():
    today = datetime.datetime.now()
    print(today)
    
    print('scheduled job active')
    products_obj = Watchlist.objects.all()
    for product in products_obj:
        user_data = User.objects.get(id=product.user_id)
        page = requests.get(url=product.product_url)
        # gathering data from server 
        time.sleep(20)   # a twenty second delay before each request so we dont overwhelm the server.
        product_data_from_server = get_product_info(page_=page,url_=product.product_url)   # 'product_data_from_server'  will contain a dictionary
        # print(product.price)
        # print(' from server ')
        # print(product_data_from_server.get('price'))

        new_price = product_data_from_server.get('price')
        new_price_th = product_data_from_server.get('price_th')
        new_availability = product_data_from_server.get('availability')

        p= products_obj.get(id=product.id)
        p.price = new_price
        p.price_th = new_price_th
        p.availability = new_availability
        p.save()    # update the newly gathered data to the database.
        print('save to DB ok')

        avilable_bool = new_availability == 'In stock'
        mailer_dict = {
                    'user':user_data,
                    'product':product,
                    'price':new_price,
                    'price_th':new_price_th,
                     }

        if ((avilable_bool and product.availability != 'In stock') and (new_price < product.price)):
            mailer_dict['is_price_drop_and_avail'] = True
            mailer_obj = MailingList(**mailer_dict)
            mailer_obj.save()

        elif avilable_bool and product.availability != 'In stock':
            mailer_dict['is_avail'] = True
            mailer_obj = MailingList(**mailer_dict)
            mailer_obj.save()

        elif new_price < product.price :
            mailer_dict['is_price_drop'] = True
            mailer_obj = MailingList(**mailer_dict)
            mailer_obj.save()

        else:
            pass
        # if end
    # loop end
    mailer() # call mailer and send mails to users in mailing list
    print('Scheduled run finished')




def mailer():
    print('Mailer service active')
    mailer_obj = MailingList.objects.filter(status = 'pending')
    for mail in mailer_obj:
        user_id = mail.user_id
        product_id = mail.product_id
        user_obj = User.objects.get(id=user_id)
        product_obj = Watchlist.objects.get(id=product_id)

        subject = ''
        message = ''
        email_from = settings.EMAIL_HOST_USER
        email_to = [user_obj.email,]

        if mail.is_price_drop_and_avail:
                subject = product_obj.product_name+' is back in stock'
                message =f'''Hai {user_obj.username},
                An item in your watchlist is now available with a pricedrop,
                check it now...
                Item name :{product_obj.product_name}
                Price Today :{str(mail.price)}(last check on {str(datetime.datetime.now())})
                product link :{product_obj.product_url}

                from pricedrop team :-)
                '''
                send_mail(subject,message,email_from,email_to)

        elif mail.is_avail:
            #send mail about product availability
            subject = product_obj.product_name+' is back in stock'
            message =f'''Hai {user_obj.username},
                An item in your watchlist is back in stock,
                check it now...
                Item name :{product_obj.product_name}
                Price Today :{str(mail.price)}(last check on {str(datetime.datetime.now())})
                product link :{product_obj.product_url}

                from pricedrop team :-)
                '''
            send_mail(subject,message,email_from,email_to)

        elif mail.is_price_drop:
            subject = '[Price Drop]-'+product_obj.product_name+'. Is now at '+str(mail.price_th)

            message =f'''Hai {user_obj.username},
                An item in your watchlist is at a lowest price,
                check it now...
                Item name :{product_obj.product_name}
                Price Today :{str(mail.price_th)}(last check on {str(datetime.datetime.now())})
                product link :{product_obj.product_url}

                from pricedrop team :-)
                '''
            send_mail(subject,message,email_from,email_to)
            
        else:
            pass
    
        mail.status='sent'
        mail.save()
    # loop end


def start():
    tz= get_localzone()
    print(tz)
    scheduler = BackgroundScheduler({'apscheduler.timezone':tz})
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 8 hours .....
    scheduler.add_job(database_crawler, 'interval', hours=8, name='DB crawling and mailer', jobstore='default')

    register_events(scheduler)
    scheduler.start()
    scheduler.print_jobs()
    print("Scheduler started...", file=sys.stdout)