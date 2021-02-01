# Backend-Test-Aleman

This technical test requires the design and implementation (using Django) of a management system to coordinate the meal delivery for Cornershop employees.

#### Contacts:
* Rodrigo Aleman: rabcr.14@gmail.com


## Installation guidelines

#### Prerequisites:
- Python 3.7 or above

#### Dependencies:
- Slack Client

#### Installation instructions:
- Create and activate env
- Config your slack settings
- Run:
  * `pip install -r requirements.txt`
  * `python manage.py makemigrations`
  * `python manage.py migrate`
  * `python manage.py collectstatic`
  * `python manage.py runserver`
- Optional (load users and dishes):
  * `python manage.py loaddata ../dump/users.json` (login password is 1234)
  * `python manage.py loaddata ../dump/dishes.json`

#### Deployment instructions:
Using Heroku

- Create and activate env
  * `Create an account and install the heroku CLI`
- Install psycopg2 and gunicorn:
  * `pip install psycopg2-binary gunicorn`
- Save requirements:
  * `pip freeze > requirements.txt`
- Init Heroku repository:
  * `git init`  
- Load statics from S3
  * Create a public bucket
  * Configure AWS credentials in settings file
- Copy files from `release` folder to the `manage.py` folder level
- Push to heroku master repository:
  * `git add -A`
  * `git commit -m "v<your version>"`
  * `heroku create`
  * `git push heroku master`

### Database configuration
Using sqlite3, no configuration required

#### Env Settings
* ALLOWED_HOUR_TO_ORDER: `Time after users cannot order, default 11`
* SLACK_API_TOKEN: `Slack bot api token`
* CHANNEL: `Channel where the slack bot app is installed, default '#general'`

#### Test coverage
Run:
  * `coverage run manage.py test -v 2`

#### Deployed app
* Url: `https://serene-wildwood-71868.herokuapp.com/`
* Admin/Nora username: `nora`
* Admin/Nora password: `1234`
* Users: [`rodrigo, pepe, ale, osvaldo`] - passwords: `1234`
* Subscribe to Slack app through: `https://join.slack.com/t/personal-xkc5415/shared_invite/zt-lfvpsgpj-x9wfwQbGfo0zvQMgkBJAiA`
* Slack app: `https://personal-xkc5415.slack.com/`

### Notes

The password in the users dump is encrypted, So when login use 1234 as password for all users.


