# Price-drop-alert
This is a simple price drop alert system made with Django.    

## Working

- User first register
- Then login
- _User may enter a product URL copied from flipkart._
- All URLs in the watchlist are scraped every time the scheduler runs.
- User will get an email when the product experiences a price drop 

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
### 1) Add a `.env` file in 'pricedrop' folder with following contents
```
EMAIL_HOST_USER = "replace your email id here"
EMAIL_HOST_PASSWORD = "your password"
```
_also enable less secure app access in google account_

### 2) Create a MySQL data base named 'django_pricedrop_db'
The database used is MySQL due to limitations in SQLite.    

### 3) Comment the ready() method in 'linkadd/apps.py'
This is to prevent "Table 'django_pricedrop_db.django_apscheduler_djangojob' doesn't exist"  error
```
    # def ready(self):
    #         from .scheduler import scheduler
    #         scheduler.start()
```
### 4) Migrate the database
```
python manage.py makemigrations
```
then
```
python manage.py migrate
```
### 5) Final step , Uncomment the ready() method in 'linkadd/apps.py'
as below
This is to start the periodic scheduler
```
    def ready(self):
            from .scheduler import scheduler
            scheduler.start()
```

## Running
For running use
```
python manage.py runserver --noreload
```
 **use   --noreload otherwise scheduler will run twice**

# Disclaimer

Web scraping and crawling aren't illegal, but scraping a website without the owners permission is not legal.

**Use it only for educational** purpose and **don't overwhelm the servers** by sending mass requests.