###############
django CMS demo
###############

|Build Status| |Coverage Status| |Code Climate| |Requirements Status|

|Browser Matrix|

The aim of this project is to run django CMS with standard configurations
including demo content and helpful addons. You can use this repository for
tutorial, debugging, development and research purposes.

We are using `Aldryn Boilerplate Bootstrap 3
<github.com/aldryn/aldryn-boilerplate-bootstrap3>`_ as the base
starting point for frontend development. Please consult the
`documentation <https://aldryn-boilerplate-bootstrap3.readthedocs.org/en/latest/>`_
for further help.

The following addons are available through this installation:

- `Aldryn Bootstrap 3 <https://github.com/aldryn/aldryn-bootstrap3>`_
- `Aldryn Blueprint <https://github.com/aldryn/aldryn-blueprint>`_ (tba)
- `Aldryn Events <https://github.com/aldryn/aldryn-events>`_
- `Aldryn FAQ <https://github.com/aldryn/aldryn-faq>`_
- `Aldryn Forms <https://github.com/aldryn/aldryn-forms>`_ (tba)
- `Aldryn Jobs <https://github.com/aldryn/aldryn-jobs>`_
- `Aldryn News & Blog <https://github.com/aldryn/aldryn-newsblog>`_
- `Aldryn Segmentation <https://github.com/aldryn/aldryn-segmentation>`_ (tba)
- `Aldryn Style <https://github.com/aldryn/aldryn-style>`_


************
Installation
************

Virtualenv
----------

- run ``make install`` to get started
- run ``make run`` to start the development server

- run ``make update`` to update the project (this will not load new static files from the Aldryn site)

Docker
------

- run ``make docker`` which sets the docker image up and runs it in the background

For additional information checkout the ``Makefile``.


***********
Development
***********

To get the tutorial experience from the django documentations just ``cd``
into ``src`` and run the usual commands (``python manage.py startapp...``).


*****
Login
*****

You can login to the cms by appending ``/?edit`` to the url. The credentials are:

- Username: **admin**
- Password: **admin**


.. |Build Status| image:: https://travis-ci.org/divio/django-cms-demo.svg?branch=master
   :target: https://travis-ci.org/divio/django-cms-demo
.. |Coverage Status| image:: https://codeclimate.com/github/divio/django-cms-demo/badges/coverage.svg
   :target: https://codeclimate.com/github/divio/django-cms-demo/coverage
.. |Code Climate| image:: https://codeclimate.com/github/divio/django-cms-demo/badges/gpa.svg
   :target: https://codeclimate.com/github/divio/django-cms-demo
.. |Requirements Status| image:: https://requires.io/github/divio/django-cms-demo/requirements.svg?branch=master
   :target: https://requires.io/github/divio/django-cms-demo/requirements/?branch=master
.. |Browser Matrix| image:: https://saucelabs.com/browser-matrix/django-cms-demo.svg
   :target: https://saucelabs.com/u/django-cms-demo
