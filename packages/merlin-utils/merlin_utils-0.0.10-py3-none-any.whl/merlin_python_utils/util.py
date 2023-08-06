import logging
import os
from functools import wraps

from flask import request
from google.auth.transport import requests
from google.oauth2 import id_token

HTTP_REQUEST = requests.Request()
PROJECT_ID = os.environ.get('project')


def firebase_auth(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        id_token_firebase = request.headers.get('Authorization')
        if not id_token_firebase:
            return 401, 'Unauthorized'
        try:
            claims = id_token.verify_firebase_token(id_token_firebase.split(' ').pop(), HTTP_REQUEST)
        except Exception as ex:
            logging.warning(ex.message)
            return 'Unauthorized', 401
        logging.info(claims)
        if not (claims.get('aud') == PROJECT_ID or claims.get('iss') == os.environ.get('issuer') % PROJECT_ID):
            return 'Unauthorized', 401
        kwargs["auth_user"] = {"id": claims.get('sub'), "role": claims.get('role')}
        return f(*args, **kwargs)

    return wrapped


def api_key(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        key = request.headers.get('api_key')
        logging.info(key)
        # TODO: Make an api_key restriction
        return f(*args, **kwargs)

    return wrapped
