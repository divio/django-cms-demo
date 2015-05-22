SHELL := /bin/bash
CHDIR_SHELL := $(SHELL)

##### SETTINGS
NAME = xplorer-standardsite-minimalistic
PORT = 8000
# local db settings
DBNAME = $(NAME)_local
DBUSER = postgres

##### VARIABLES
ENV = .virtualenv
VENV = $(ENV)/bin/activate
PTYHON = $(ENV)/bin/python
PIP = $(ENV)/bin/pip
PROJECT_DIR = ./site
BRANCH=`git branch --no-color 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/'`


##### REQUIRED COMMANDS
##### https://github.com/divio/divio-architect
##### You need to be within the repository for excecution
all:
	##### automatically run the project with all requirements
	make -j4 server tasks css

install:
	test -d $(VENV) || virtualenv $(ENV) --prompt="(`basename \`pwd\``)"
	##### install python requirements
	. $(VENV); $(PIP) install -r $(PROJECT_DIR)/requirements.txt
	. $(VENV); npm install
	##### install gem requirements
	make gems
	##### create database
	-psql -U $(DBUSER) -c 'DROP DATABASE $(DBNAME);'
	psql -U $(DBUSER) -c 'CREATE DATABASE $(DBNAME);'
	#### install data
	$(MANAGE) dbshell < ./database.sql
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

run:
	make -j4 server


##### HELPER COMMANDS
##### helpers and other non-related commands omitted from divio-architect
server:
	$(PTYHON) $(PROJECT_DIR)/manage.py runserver 0.0.0.0:$(PORT)

tasks:
	. $(VENV); gulp

css:
	. $(VENV); compass watch private --sourcemap

cssforce:
	. $(VENV); compass compile private --sourcemap --force

gems:
	grep -q ". $(PWD)/.gemenv" virtualenv/bin/activate || echo ". $(PWD)/.gemenv" >> virtualenv/bin/activate
	. $(VENV); gem install bundler --no-rdoc --no-ri
	. $(VENV); bundle install --binstubs $(ENV)/bin --clean --path $(ENV)/gems
