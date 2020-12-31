# Price-drop-alert
This is a simple price drop alert system made with django.    
_Users may enter a product url copied from flipkart._

## Dependencies
Install dependencies beforehand. 
```
pip install django-apscheduler
```
```
pip install beautifulsoup4
```
```
pip install requests
```

# Quick setup before running
Add a `.env` file in pricedrop/ folder with following contents
```
EMAIL_HOST_USER = "replace your email id here"
EMAIL_HOST_PASSWORD = "your password"
```
_also enable less secure app access in google account_

## Running
For running use
```
python manage.py runserver --noreload
```
 **use --noreload otherwise scheduler will run twice**
