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
	make update
	make reset

run:
	make -j4 css runserver

update:
	-git pull
	$(PIP) install -r requirements.txt
	$(VENV); npm install
	$(MANAGE) migrate


##### HELPER COMMANDS
##### helpers and other non-related commands omitted from divio-architect

reset:
	-psql -U $(DBUSER) -c 'DROP DATABASE $(DBNAME);'
	psql -U $(DBUSER) -c 'CREATE DATABASE $(DBNAME);'
	unzip database.sql.zip
	$(VENV); $(MANAGE) dbshell < database.sql
	rm database.sql

full_reset:
	rm -rf env/
	make reset

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
