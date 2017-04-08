###############
django CMS demo
###############

|build| |coverage|

**django CMS Demo** is no traditional "Demo" project for presentational usage.
It is aimed for developers who want to test the latest django CMS and addon
versions, living on the edge. This means, that the project setup can be unstable
from time to time.

Please only use this repository for debugging, development and research
purposes. **This codebase is not meant to be used in production**.

* **Django 1.10**
* **django CMS develop branch**


============
Installation
============

Virtualenv
----------

- run ``virtualenv env`` to create a virtual environment
- run ``source env/bin/activate`` to start the virtual environment
- run ``pip install -r requirements.txt`` to install all requirements
- run ``python manage.py migrate`` to run database migrations
- run ``python manage.py loaddata data.json`` to load the admin user,
  you can also create your own by running ``python manage.py createsuperuser`` instead
- run ``python manage.py runserver 0.0.0.0:8000`` to start the local development server
- visit ``http://localhost:8000``

Docker
------

- run ``docker build -t divio/django-cms-demo .`` to build the image
- run ``docker run -it -p 8000:8000 divio/django-cms-demo`` to start the container
- visit ``http://localhost:8000`` (depending on your docker configuration)

Login
-----

You can login to the cms by appending ``/?edit`` to the url. The credentials are:

- Username: **admin**
- Password: **admin**


.. |build| image:: https://travis-ci.org/divio/django-cms-demo.svg?branch=master
    :target: https://travis-ci.org/divio/django-cms-demo
.. |coverage| image:: https://codecov.io/gh/divio/django-cms-demo/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/divio/django-cms-demo
