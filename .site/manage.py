#!/usr/bin/env python
from django.core.management import ManagementUtility
import os

import dotenv
from getenv import env
dotenv.read_dotenv()
try:
    dotenv.read_dotenv('.env')
except:
    pass


if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = env('DJANGO_SETTINGS_MODULE', 'settings')
    utility = ManagementUtility(None)
    utility.execute()
