"""
File:           wsgi.py
Author:         Dibyaranjan Sathua
Created on:     22/02/21, 10:19 pm
"""
from app import app, AppLayout


def create_app():
    """ Create the app and running app using gunicorn """
    AppLayout().setup()
    return app.server
