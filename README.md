# Wallets App REST API made on Django Rest Framework

The app allows to:
  * create wallets
  * get wallets
  * make deposits
  * make transfers
  * get filtered wallet's transactions history both in .csv or json formats
  
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
```

Sample .env.db configuration:
```
POSTGRES_USER=postgres_admin
POSTGRES_PASSWORD=postgres_password
POSTGRES_DB=postgres_db
```
