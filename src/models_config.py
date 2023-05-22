from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class DataError(Exception):
    """ Errors refered to data validation"""
    pass

class ServerError(Exception):
    """ Errors refered to data validation"""
    pass

class AuthorizationError(Exception):
    """ Errors refered Authorization"""
    pass