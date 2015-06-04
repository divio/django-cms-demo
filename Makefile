SHELL := /bin/bash

ENV = env
VENV = source $(ENV)/bin/activate
PIP = $(VENV); $(ENV)/bin/pip
MANAGE = $(VENV); $(ENV)/bin/python src/manage.py
DBUSER = postgres
DBNAME = djangocms_demo_local

install:
	virtualenv $(ENV)
	$(PIP) install -r requirements.txt
	make reset

update:
	$(MANAGE) syncdb
	$(MANAGE) migrate
	$(PIP) install -r requirements.txt --upgrade

reset:
	-psql -U $(DBUSER) -c 'DROP DATABASE $(DBNAME);'
	psql -U $(DBUSER) -c 'CREATE DATABASE $(DBNAME);'
	unzip ./database.sql.zip
	$(VENV); $(MANAGE) dbshell < ./database.sql
	rm ./database.sql
