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
	make -j css runserver

update:
	-git pull
	$(PIP) install -r requirements.txt
	$(VENV); npm install
	gulp sass
	make migrate

pulldata:
	$(MANAGE) migrate --noinput

tests:
	gulp tests

##### HELPER COMMANDS
##### helpers and other non-related commands omitted from divio-architect

# recreate the entire project and run installation
nuke:
	rm -rf env/
	rm -rf data/
	rm -rf node_modules/
	rm -rf static/css/
	make install

database:
	-psql -U $(DBUSER) -c 'DROP DATABASE $(DBNAME);'
	psql -U $(DBUSER) -c 'CREATE DATABASE $(DBNAME);'

migrate:
	$(MANAGE) migrate --noinput --no-initial-data

dump:
	$(MANAGE) dumpdata -e contenttypes -e admin -e auth.permission --natural --indent=4 > initial_data.json

runserver:
	$(MANAGE) runserver 0.0.0.0:$(PORT)

css:
	$(VENV); gulp sass
	$(VENV); gulp watch

##### DOCKER INTEGRATION
##### requires docker-compose http://docs.docker.com/compose/install/
DOCKER_IP = `boot2docker ip`

docker:
	make docker_install
	make docker_run
	make docker_pulldata
	make docker_ip

docker_install:
	docker-compose stop
	docker-compose rm --force -v
	docker-compose build

docker_database:
	docker-compose run web src/manage.py migrate --noinput

docker_node:
	docker-compose run nodejs npm install gulp
	docker-compose run nodejs npm install

docker_run:
	docker-compose up -d

docker_pulldata:
	unzip database.sql.zip
	docker-compose run web src/manage.py dbshell < database.sql
	rm -rf database.sql

docker_ip:
	docker-compose ps
	@echo --------------------------------------------------
	@echo SERVER RUNNING ON: $(DOCKER_IP):$(PORT)
	@echo --------------------------------------------------
