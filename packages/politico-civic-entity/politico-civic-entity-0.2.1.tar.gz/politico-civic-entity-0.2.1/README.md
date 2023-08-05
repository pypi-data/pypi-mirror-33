![POLITICO](https://rawgithub.com/The-Politico/src/master/images/logo/badge.png)

# django-politico-civic-entity

Manage political people and organizations, the POLITICO way.

### Quickstart

1. Install the app.

  ```
  $ pip install django-politico-civic-entity
  ```

2. Add the app to your Django project settings and configure app settings.

  ```python
  INSTALLED_APPS = [
      # ...
      'rest_framework',
      'entity',
  ]

  #########################
  # entity settings

  ENTITY_AWS_ACCESS_KEY_ID = ''
  ENTITY_AWS_SECRET_ACCESS_KEY = ''
  ENTITY_AWS_S3_BUCKET = ''
  ENTITY_CLOUDFRONT_ALTERNATE_DOMAIN = ''
  ENTITY_S3_UPLOAD_ROOT = 'uploads/entity' # default
  ENTITY_AWS_S3_ACL = 'public-read' # default
  ENTITY_API_AUTHENTICATION_CLASS = 'rest_framework.authentication.BasicAuthentication' # default
  ENTITY_API_PERMISSION_CLASS = 'rest_framework.permissions.IsAdminUser' # default
  ENTITY_API_PAGINATION_CLASS = 'geography.pagination.ResultsPagination' # default

  ```

3. Migrate the database

  ```
  $ python manage.py migrate entity
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
  DATABASE_URL="postgres://localhost:5432/entity"
  ```

3. Run migrations from the example app.

  ```
  $ cd example
  $ pipenv run python manage.py migrate
  ```
