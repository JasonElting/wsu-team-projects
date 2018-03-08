import sys, os

# To include the application's path in the Python search path
sys.path.insert(1, os.path.dirname(__file__))
# print(sys.path)

# Construct a Flask instance "app" via package mypack's __init__.py
from mypack import app as application
