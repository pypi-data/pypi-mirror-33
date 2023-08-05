from werkzeug.local import LocalProxy
from flask import _request_ctx_stack


current_token = LocalProxy(lambda: getattr(_request_ctx_stack.top,
                                           "current_token", None))
