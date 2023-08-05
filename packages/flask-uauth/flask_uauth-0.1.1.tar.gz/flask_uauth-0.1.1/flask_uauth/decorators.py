from functools import wraps

from flask import request, current_app
from flask import _request_ctx_stack


def authentication_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        uauth = current_app.extensions["uauth"]
        token = uauth.authenticate_request(request)

        _request_ctx_stack.top.current_token = token

        return f(*args, **kwargs)
    return wrapper
