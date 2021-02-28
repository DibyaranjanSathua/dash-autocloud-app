"""
File:           wsgi.py
Author:         Dibyaranjan Sathua
Created on:     22/02/21, 10:19 pm
"""
from app import AppLayout


def create_app():
    """ Create the app and running app using gunicorn """
    return AppLayout().setup()


if __name__ == "__main__":
    create_app()
