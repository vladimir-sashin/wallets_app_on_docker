# Wallets App REST API made on Django Rest Framework

A stack used:
  * Django Rest Framework
  * PostgreSQL
  * Gunicorn
  * Nginx
  * Celery
  * RabbitMQ as message broker
  * Sentry as application monitoring and error tracking system

The app allows to:
  * register users and login using JWT authentication
  * create wallets
  * get paginated list of all user's wallets, or wallet details
  * make deposits
  * make transfers
  * get filtered wallet's transactions history both in .csv or json formats (paginated in case of json) depending on 
   ```Accept``` HTTP Header

Additional features:
  * Celery + RabbitMQ are used to calculate reports for every wallet with sums of incoming and outgoing transactions 
    that were made today. This task runs every 10 minutes. If it fails, it retries up to 3 times with initial delay of
    10 seconds that increases by 2 times every fail.
  * Super user may access these reports by GET /api/reports/ requests or at /admin tab in the TransactionReport table
  * Sentry is configured as monitoring and error tracking software. Sentry DSN URL needs to be included in .env file, 
    as in example below.

Sample .env configuration:
```
DEBUG=1
SECRET_KEY=foo
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=postgres_db
SQL_USER=postgres_admin
SQL_PASSWORD=postgres_password
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres
DISABLE_SERVER_SIDE_CURSORS=True
SENTRY_DSN=insert_your_sentry_dsn_url_here
```

Sample .env.db configuration:
```
POSTGRES_USER=postgres_admin
POSTGRES_PASSWORD=postgres_password
POSTGRES_DB=postgres_db
```

To run the application:
1. Clone the repo
2. Run ```docker-compose build```
3. Run ```docker-compose up```
4. Enjoy the app on http://localhost:1337/
5. Swagger API documentation is available on http://localhost:1337/api/schema/swagger-ui/