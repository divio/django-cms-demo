FROM python:2.7

ENV DJANGO_SETTINGS_MODULE settings

ADD . /project
WORKDIR /project

RUN pip install -r requirements.txt

EXPOSE 80

CMD python src/manage.py runserver 0.0.0.0:80
