SHELL := /bin/bash

PORT = 8000
ENV = env
VENV = source $(ENV)/bin/activate
PIP = $(VENV); $(ENV)/bin/pip
MANAGE = $(VENV); $(ENV)/bin/python manage.py
DBUSER = postgres
DBNAME = djangocms_demo_local


##### REQUIRED COMMANDS
##### https://github.com/divio/divio-architect
##### You need to be within the repository for excecution

all:
	make run

install:
	virtualenv $(ENV)
	make theme
	make database
	make update
	make pulldata

run:
	make -j css runserver

update:
	-git pull
	$(PIP) install -r requirements.txt --no-cache
	$(VENV); npm install
	gulp sass
	make migrate

pulldata:
	$(MANAGE) migrate --noinput

tests:
	gulp tests

nuke:
	make clean
	make install

##### HELPER COMMANDS
##### helpers and other non-related commands omitted from divio-architect

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

theme:
	curl -LOk https://github.com/divio/django-cms-explorer/archive/master.tar.gz
	tar -xzf master.tar.gz
	mv -n django-cms-explorer-master/{*,.*} .
	rm -rf django-cms-explorer-master/ ./master.tar.gz

clean:
	# cleaning theme files
	rm -rf private/ static/ templates/ tools/ tests/ browserslist gulpfile.js
	rm -rf .bowerrc .csscomb.json .jscsrc .jshintrc bower.json package.json
	# cleaning remainings
	rm -rf env/ data/ node_modules/ static/css/
	# remove pyc files
	find . -name '*.pyc' -delete


##### DOCKER INTEGRATION
##### requires docker-compose http://docs.docker.com/compose/install/
DOCKER_IP = `docker-machine ip default`

docker:
	make docker_install
	make docker_run
	make docker_database
	make docker_pulldata
	make docker_ip

docker_install:
	docker-compose stop
	docker-compose rm -f -v
	docker-compose build

docker_run:
	docker-compose up -d
	sleep 5

docker_database:
	docker-compose run web python manage.py migrate --noinput --no-initial-data

docker_pulldata:
	docker-compose run web python manage.py migrate --noinput

docker_ip:
	docker-compose ps
	@echo ---------------------------------------------
	@echo SERVER RUNNING ON: $(DOCKER_IP):$(PORT)
	@echo ---------------------------------------------
