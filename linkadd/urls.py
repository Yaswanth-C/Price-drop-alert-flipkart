"""linkadd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

app_name="linkadd"

urlpatterns = [
    path(
        route='add/',
        view=views.link_add_view,
        name="add_link_to_wl",
    ),
    path(
        route='add/add_link',
        view=views.link_add_ajax,
        name="add_link_ajax",
    ),
    path(
        roure='view/',
        view=views.view_watch_list,
        name="view_watchlist",
    ),
    path(
        roure='save/',
        view=views.save_last_search,
        name='save_to_list',
    ),
    path(
        roure='delete/<int:id>/',
        view=views.delete_watchlist_item,
        name='delete_item',
    ),
    path(
        route='view_history/<int:id>/',
        view=views.view_prod_history,
        name='view_history',
    ),
]