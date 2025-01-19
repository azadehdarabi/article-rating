### Getting started

- Copy & update environment variables from `.env.sample`
  ```shell
  cp .env.sample .env
   ```
- Apply migrations
  ```shell
  python manage.py migrate
  ```
- Happy coding!!!

### Advanced:

- Install dependencies for Python 3.12
  ```shell
  pip install -r requirements.txt
  ```
- Make new migrations
  ```shell
  python manage.py makemigrations
  ```
- Run tests with full detail for api
  ```shell
  python manage.py test
  ```
  