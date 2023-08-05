![POLITICO](https://rawgithub.com/The-Politico/src/master/images/logo/badge.png)

# django-politico-civic-election

Create and manage election metadata, the POLITICO way.

### Quickstart

1. Install the app.

  ```
  $ pip install django-politico-civic-election
  ```

2. Add the app and its dependencies to your Django project.

  ```python
  INSTALLED_APPS = [
      # ...
      'rest_framework',
      'entity',
      'geography',
      'government',
      'election',
  ]

  #########################
  # election settings

  ELECTION_API_AUTHENTICATION_CLASS = 'rest_framework.authentication.BasicAuthentication' # default
  ELECTION_API_PERMISSION_CLASS = 'rest_framework.permissions.IsAdminUser' # default
  ELECTION_API_PAGINATION_CLASS = 'election.pagination.ResultsPagination' # default
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
  DATABASE_URL="postgres://localhost:5432/election"
  ```

3. Run migrations from the example app.

  ```
  $ cd example
  $ pipenv run python manage.py migrate
  ```
