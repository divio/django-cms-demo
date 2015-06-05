#######################
django CMS demo project
#######################


The aim of this project is to run django CMS with simple configurations and demo content.
You can use this repository for debugging, development and research purposes on the backend or frontend-stack.

The following addons are available through this installation:

- `Aldryn Blueprint <https://github.com/aldryn/aldryn-blueprint>`_ (tba)
- `Aldryn Bootstrap3 <https://github.com/aldryn/aldryn-bootstrap3>`_ (tba)
- `Aldryn Forms <https://github.com/aldryn/aldryn-forms>`_ (tba)
- `Aldryn Segmentation <https://github.com/aldryn/aldryn-segmentation>`_ (tba)
- `Aldryn Style <https://github.com/aldryn/aldryn-style>`_ (tba)


************
Installation
************

- run ``make install`` to get started
- run ``make run`` to start the development server

- run ``make update`` to update the project (this will not load new static files from the Aldryn site)


***********
Development
***********

To get the tutorial experience from the django documentations just ``cd`` into ``src`` and
run the usual commands (``python manage.py startapp...``).


*****
Login
*****

You can login to the cms by appending ``/?edit`` to the url. The credentials are:

- Username: **admin**
- Password: **admin**
