FROM python:3.6

ENV DJANGO_SETTINGS_MODULE src.settings

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN python manage.py migrate
RUN python manage.py loaddata data.json

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000
