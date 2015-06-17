FROM python:2.7
ENV PYTHONUNBUFFERED 1

ADD . /project
WORKDIR /project

RUN pip install -r requirements.txt

CMD python src/manage.py runserver 0.0.0.0:8000

EXPOSE 8000:8000
