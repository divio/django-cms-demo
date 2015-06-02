SHELL := /bin/bash
CHDIR_SHELL := $(SHELL)

##### SETTINGS
NAME = xplorer_standardsite_minimalistic
PORT = 8000
# local db settings
DBNAME = $(NAME)_local
DBUSER = postgres

##### VARIABLES
ENV = .virtualenv
VENV = $(ENV)/bin/activate
PTYHON = $(ENV)/bin/python
PIP = $(ENV)/bin/pip
PROJECT_DIR = .site
BRANCH=`git branch --no-color 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/'`


##### REQUIRED COMMANDS
##### https://github.com/divio/divio-architect
##### You need to be within the repository for excecution
all:
	##### automatically run the project with all requirements
	make -j4 server tasks cssforce css

install:
	test -d $(VENV) || virtualenv $(ENV) --prompt="(`basename \`pwd\``)"
	##### install python requirements
	. $(VENV); $(PIP) install -r $(PROJECT_DIR)/requirements.txt
	. $(VENV); npm install
	##### we need to create an aldrynfile from
	##### https://github.com/aldryn/aldryn-client/blob/09be71543c701b293978d7829898c076a4578efb/aldryn_client/client.py#L522
	@echo $(PWD)/dev > $(ENV)/lib/python2.7/site-packages/aldrynsite_dev.pth
	##### install gem requirements
	make gems
	##### create database
	-psql -U $(DBUSER) -c 'DROP DATABASE $(DBNAME);'
	psql -U $(DBUSER) -c 'CREATE DATABASE $(DBNAME);'
	#### install data
	unzip ./database.sql.zip
	. $(VENV); $(PTYHON) $(PROJECT_DIR)/manage.py dbshell < ./database.sql
	rm ./database.sql
	#### finished

update:
	##### pull from git
	-git pull origin $(BRANCH)
	##### remove pyc files
	find . -name '*.pyc' -delete
	##### update requirements
ifdef FORCE
	. $(VENV); $(PIP) install -r $(PROJECT_DIR)/requirements.txt --upgrade
	. $(VENV); npm update
	. $(VENV); gem update -N --no-rdoc --no-ri
else
	. $(VENV); $(PIP) install -r $(PROJECT_DIR)/requirements.txt
endif
	##### update database data
	export LANG="en_US.UTF-8"
	$(PTYHON) $(PROJECT_DIR)/manage.py syncdb
	$(PTYHON) $(PROJECT_DIR)/manage.py migrate
	##### finished

reset:
	-psql -U $(DBUSER) -c 'DROP DATABASE $(DBNAME);'
	psql -U $(DBUSER) -c 'CREATE DATABASE $(DBNAME);'
	unzip ./database.sql.zip
	. $(VENV); $(PTYHON) $(PROJECT_DIR)/manage.py dbshell < ./database.sql
	rm ./database.sql

run:
	make -j4 server


##### HELPER COMMANDS
##### helpers and other non-related commands omitted from divio-architect
server:
	$(PTYHON) $(PROJECT_DIR)/manage.py runserver 0.0.0.0:$(PORT)

tasks:
	. $(VENV); gulp

css:
	. $(VENV); compass watch .site/private --sourcemap

cssforce:
	. $(VENV); compass compile private --sourcemap --force

gems:
	grep -q ". $(PWD)/.gemenv" .virtualenv/bin/activate || echo ". $(PWD)/.gemenv" >> .virtualenv/bin/activate
	. $(VENV); gem install bundler --no-rdoc --no-ri
	. $(VENV); bundle install --binstubs $(ENV)/bin --clean --path $(ENV)/gems

dump:
	rm -rf database.sql.zip
	pg_dump $(DBNAME) --file=database.sql
	zip -r database.sql.zip database.sql
	rm -rf database.sql
