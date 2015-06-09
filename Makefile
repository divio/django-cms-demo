SHELL := /bin/bash

PORT = 8000
ENV = env
VENV = source $(ENV)/bin/activate
PIP = $(VENV); $(ENV)/bin/pip
MANAGE = $(VENV); $(ENV)/bin/python src/manage.py
DBUSER = postgres
DBNAME = djangocms_demo_local


##### REQUIRED COMMANDS
##### https://github.com/divio/divio-architect
##### You need to be within the repository for excecution

all:
	make run

install:
	virtualenv $(ENV)
	make database
	make update
	make pulldata

run:
	make -j4 css runserver

update:
	-git pull
	$(PIP) install -r requirements.txt
	$(VENV); npm install
	$(MANAGE) migrate --noinput

pulldata:
	make database
	unzip database.sql.zip
	$(VENV); $(MANAGE) dbshell < database.sql
	rm database.sql


##### HELPER COMMANDS
##### helpers and other non-related commands omitted from divio-architect

# recreate the entire project WITHOUT data
nuke:
	rm -rf env/
	rm -rf data/
	rm -rf node_modules/
	rm -rf static/css/
	make install

database:
	-psql -U $(DBUSER) -c 'DROP DATABASE $(DBNAME);'
	psql -U $(DBUSER) -c 'CREATE DATABASE $(DBNAME);'

dump:
	rm -rf database.sql.zip
	pg_dump $(DBNAME) --file=database.sql
	zip -r database.sql.zip database.sql
	rm -rf database.sql

runserver:
	$(MANAGE) runserver 0.0.0.0:$(PORT)

css:
	$(VENV); gulp sass
	$(VENV); gulp watch
