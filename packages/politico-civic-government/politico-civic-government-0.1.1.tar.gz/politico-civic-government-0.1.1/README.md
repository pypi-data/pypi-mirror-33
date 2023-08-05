![POLITICO](https://rawgithub.com/The-Politico/src/master/images/logo/badge.png)

# django-politico-civic-government

Create and manage the basic structure of federal, state and local government, the POLITICO way.

### Quickstart

1. Install the app.

  ```
  $ pip install django-politico-civic-government
  ```

2. Add the app and dependencies to your Django project and configure any needed settings.

  ```python
  INSTALLED_APPS = [
      # ...
      'rest_framework',
      'entity',
      'geography',
      'government',
  ]

  #########################
  # government settings

  GEOGRAPHY_API_AUTHENTICATION_CLASS = 'rest_framework.authentication.BasicAuthentication' # default
  GEOGRAPHY_API_PERMISSION_CLASS = 'rest_framework.permissions.IsAdminUser' # default
  GEOGRAPHY_API_PAGINATION_CLASS = 'government.pagination.ResultsPagination' # default
  ```

### Bootstrapping your database

**NOTE:** These commands must be run **AFTER** `bootstrap_geography` from the `django-politico-civic-geography` package.

##### Bootstrap the Federal Government

```
$ python manage.py bootstrap_fed
```

##### Bootstrap major political parties

```
$ python manage.py bootstrap_parties
```

##### Bootstrap state jurisdictions

```
$ python manage.py bootstrap_jurisdiction
```

### Developing

##### Running a development server

Move into the example directory, install dependencies and run the development server with pipenv.

  ```
  $ cd example
  $ pipenv install
  $ pipenv run python manage.py runserver
  ```

##### Setting up a PostgreSQL database

1. Run the make command to setup a fresh database.

  ```
  $ make database
  ```

2. Add a connection URL to `example/.env`.

  ```
  DATABASE_URL="postgres://localhost:5432/government"
  ```

3. Run migrations from the example app.

  ```
  $ cd example
  $ pipenv run python manage.py migrate
  ```
