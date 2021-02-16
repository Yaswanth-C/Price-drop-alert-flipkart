# Price-drop-alert
This is a simple price drop alert system made with Django.    

## Working

- User needs to register first, with an email id of their choice .
- Then login with the registered credentials.
- User may enter a product URL copied from flipkart ,then check the response and add it to the watchlist.
- All URLs in the watchlist are scraped every time the scheduler runs.
- Changes to the price or availability of the product is then saved to the database.
- User will get an email when the product experiences a price drop or whenever the product is back in stock.

## Dependencies
Install dependencies beforehand. 
```
pip install -r requirements.txt
```
# Quick setup before running
### 1) Add a `.env` file in 'pricedrop' folder with following contents
```
EMAIL_HOST_USER = "replace this with the email-id( Gmail id ) you are going to use."
EMAIL_HOST_PASSWORD = "the google account password"
```
<mark>**_Note:_** This Email-id and password(must be a Gmail one) is for the system to mail the alerts to the users. The registering users must enter their email-id on the sign-up page.</mark>

_Also enable <mark>less secure app access</mark> in google account_

### 2) Create a MySQL data base named 'django_pricedrop_db'
The database used is MySQL due to limitations in SQLite.    

### 3) Comment the ready() method in 'linkadd/apps.py'
This is to prevent "Table 'django_pricedrop_db.django_apscheduler_djangojob' doesn't exist"  error when migrating the database.
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
