FROM python:2.7

ENV DJANGO_SETTINGS_MODULE settings

ADD . /project
WORKDIR /project

RUN apt-get -y update
RUN apt-get -y install postgresql-client
RUN pip install -r requirements.txt

EXPOSE 80

CMD python src/manage.py runserver 0.0.0.0:80
