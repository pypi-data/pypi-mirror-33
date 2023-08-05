![POLITICO](https://rawgithub.com/The-Politico/src/master/images/logo/badge.png)

# django-politico-civic-election-night

### Quickstart

1. Install the app.

  ```
  $ pip install django-politico-civic-election-night
  ```

2. Add the app to your Django project and configure settings.

  ```python
  INSTALLED_APPS = [
      # ...
      'rest_framework',
      'electionnight',
  ]

  #########################
  # electionnight settings

  ELECTIONNIGHT_SECRET_KEY = ''
  ELECTIONNIGHT_AWS_ACCESS_KEY_ID = ''
  ELECTIONNIGHT_AWS_SECRET_ACCESS_KEY = ''
  ELECTIONNIGHT_AWS_REGION = ''
  ELECTIONNIGHT_AWS_S3_BUCKET = ''
  ELECTIONNIGHT_CLOUDFRONT_ALTERNATE_DOMAIN = ''
  ELECTIONNIGHT_S3_UPLOAD_ROOT = ''
  ```

### Developing

##### Running a development server

Developing python files? Move into example directory and run the development server with pipenv.

  ```
  $ cd example
  $ pipenv run python manage.py runserver
  ```

Developing static assets? Move into the pluggable app's staticapp directory and start the node development server, which will automatically proxy Django's development server.

  ```
  $ cd electionnight/staticapp
  $ gulp
  ```

Want to not worry about it? Use the shortcut make command.

  ```
  $ make dev
  ```

##### Setting up a PostgreSQL database

1. Run the make command to setup a fresh database.

  ```
  $ make database
  ```

2. Add a connection URL to the `.env` file.

  ```
  DATABASE_URL="postgres://localhost:5432/electionnight"
  ```

3. Run migrations from the example app.

  ```
  $ cd example
  $ pipenv run python manage.py migrate
  ```


##### Running results

1. Make sure you have `AP_API_KEY` in your `.env` file.

2. Make sure your election models are hydrated.

  ```
  $ cd example
  $ python manage.py bootstrap_election_events
  $ python manage.py bootstrap_elections
  $ python manage.py bootstrap_elex <election-date>
  ```

3. Build the config files

  ```
  $ cd example
  $ python manage.py bootstrap_results_config <election-date>
  ```

4. Get results

  ```
  $ python manage.py get_results <election-date> --test --run_once
  ```