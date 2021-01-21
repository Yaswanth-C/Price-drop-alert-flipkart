from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Watchlist,MailingList

import requests
from . import functions
# Create your views here.

@login_required
def link_add_view(request):
    return render(request, "linkadd/add_url.html")

@login_required
def link_add_ajax(request):
    if request.is_ajax() and request.method == 'POST':
        url = request.POST.get('url','')    # user submitted product url
        try:
            page = requests.get(url=url)    # getting page data of the url
        except:
            data = {
                    'error':True,
                    'msg':'bad url'
                   }
            return JsonResponse(data,status = 400)
        slash_list = url.split('/')
        domain = slash_list[2]
        print(domain)
        if url == '' or domain != "www.flipkart.com":     
            data = {
                        'error':True,
                        'msg':'Url is bad !! .Only flipkart.com urls are supported !!'
                   }
            return JsonResponse(data,status = 400)
        else:
            status_code = str(page.status_code)
            print('status:'+status_code)
            if  status_code[0]  == '2' :
                product_details = functions.get_product_info(page_=page,url_=url,user=request.user)    # returns a dictionary to product_details
                if product_details.get('price') != 0 and product_details.get('product_name') != '':
                    request.session['product_details'] = product_details
                    # print(product_details)
                    return JsonResponse(product_details,status = 200)
                else :
                    data = {
                            'error':True,
                            'msg':'bad url!! . Please provide a valid product url'
                           }
                    return JsonResponse(data,status = 400)

            else:
                data = {
                        'error':True,
                        'msg':'url is bad or not found!!'
                       }
                return JsonResponse(data,status = 400)

@login_required
def save_last_search(request):
    try:
        product_data = request.session['product_details']
    except KeyError:
        print('no session data')
        messages.error(request,'Failed to add to watchlist')
        return redirect('add/')
    else:
        product_data.pop('exists')
        product_data['user'] = request.user
        w_list_obj = Watchlist(**product_data)
        w_list_obj.save()
        messages.success(request, 'Successfully added to watchlist')
        return redirect('watchlist:add_link_to_wl')


@login_required
def view_watch_list(request):
    obj = Watchlist.objects.filter(user=request.user)
    data=obj
    return render(request,"linkadd/view_added_items.html",{'data':data})


@login_required
def delete_watchlist_item(request,id):
    try:
        mail_lists = MailingList.objects.filter(product_id=id)
    except:
        messages.error(request,'Error while deleting..!!')
    else:
        for mail in mail_lists:
            mail.delete()
    finally:
        product = Watchlist.objects.get(id=id)
        product.delete()
    return redirect('watchlist:view_watchlist')


@login_required
def view_prod_history(request,id):
    # read db
    obj = MailingList.objects.filter(user=request.user,product_id=id)
    product_details = Watchlist.objects.get(id=id)
    return render(request,"linkadd/view_history.html",{'history':obj,'product':product_details})        
    






