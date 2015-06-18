FROM python:2.7

ADD . /project
WORKDIR /project

RUN apt-get -y update
RUN apt-get -y install postgresql-client
RUN pip install -r requirements.txt

CMD python src/manage.py runserver 0.0.0.0:8000

EXPOSE 8000
