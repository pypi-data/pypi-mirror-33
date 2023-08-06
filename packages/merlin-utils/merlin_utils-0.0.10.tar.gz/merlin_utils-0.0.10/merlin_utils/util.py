import copy
import logging
import os
import re
from datetime import datetime
from functools import wraps

from flask import request
from flask_api import status
from google.auth.transport import requests
from google.cloud.datastore import Entity
from google.oauth2 import id_token

HTTP_REQUEST = requests.Request()
PROJECT_ID = os.environ.get('PROJECT')
UNAUTH = {"Message": "User has not permissions"}, status.HTTP_401_UNAUTHORIZED


def firebase_auth(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        id_token_firebase = request.headers.get('Authorization')
        if not id_token_firebase:
            return UNAUTH
        try:
            claims = id_token.verify_firebase_token(id_token_firebase.split(' ').pop(), HTTP_REQUEST)
        except Exception as ex:
            logging.warning(ex)
            return UNAUTH
        logging.info(claims)
        if not (claims.get('aud') == PROJECT_ID or claims.get('iss') == os.environ.get('ISSUER') % PROJECT_ID):
            return UNAUTH
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


def pre_loader(in_data):
    if in_data is not None:
        if isinstance(in_data, Entity):
            in_data["key"] = in_data.key
        for key, value in copy.deepcopy(in_data).items():
            if isinstance(value, datetime):
                in_data[key] = value.isoformat()
            elif value is None:
                in_data.pop(key)


def validate_email(email):
    if email is not None:
        return email.split("@")[0] if re.fullmatch("^\w+@\w+\..{2,3}(.{2,3})?$", email) is not None else None
