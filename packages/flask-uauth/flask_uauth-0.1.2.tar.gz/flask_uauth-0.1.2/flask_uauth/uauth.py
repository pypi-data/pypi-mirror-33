from werkzeug.exceptions import Unauthorized
from flask import current_app


def _reject_unauthorized_request():
    raise Unauthorized()


class UAuth(object):
    """API Authentication extension for Flask"""

    def __init__(self, app=None, authentication_callback=None):
        """Create a new UAuth object

        :param Flask app: the Flask object on wich to use
        :param func authentication_callback: the authentication callback
        function
        """
        self.app = app
        self.authentication_callback = authentication_callback

        self.handle_unauthorized_user = _reject_unauthorized_request
        self.handle_missing_token = _reject_unauthorized_request

        if app is not None:
            self.init_app(
                app=app,
                authentication_callback=self.authentication_callback
            )

    @property
    def auth_header(self):
        """Get the header to use for authentication

        The default authentication header is 'Authorization'

        :rtype str
        :return: the authentication header
        """
        app = self._get_app()

        return app.config.get("UAUTH_AUTHENTICATION_HEADER", "Authorization")

    @property
    def auth_argument(self):
        """Get the argument to use for authentication

        :rtype: str
        :return: the authentication argument
        """
        app = self._get_app()

        return app.config.get("UAUTH_AUTHENTICATION_ARGUMENT")

    def _get_app(self):
        return self.app or current_app

    def _get_authentication_value(self, request):
        authentication_value = None

        if self.auth_header is not None:
            authentication_value = request.headers.get(self.auth_header)

        # we could not get the authentication value from a header. Lets try
        # to get it from an argument
        if authentication_value is None and self.auth_argument is not None:
            authentication_value = request.args.get(self.auth_argument)

        return authentication_value

    def init_app(self, app, authentication_callback=None):
        """Initialize the authentication extention

        :param Flask app: the Flask object on wich to use
        :param func authentication_callback: the authentication callback
        function
        """
        self.authentication_callback = (
                authentication_callback or self.authentication_callback)

        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["uauth"] = self

    def get_token(self, authorization_value):
        """Retrieve the token object

        The callback function should return None if the token doesn't exist

        :param str authorization_value: the value to use in order to search
        and retrieve the token object
        :rtype: TokenMixin|None
        :return: the Token object
        """
        return self.authentication_callback(authorization_value)

    def authenticate_request(self, request):
        """Authenticate the Flask request

        :param Request request: the Flask request object
        :rtype: TokenMixin|None
        :return: the token object
        """
        authentication_value = self._get_authentication_value(request)

        if authentication_value is None:
            return self.handle_missing_token()

        token = self.get_token(authentication_value)
        if token is None or not token.is_active():
            return self.handle_unauthorized_user()

        return token
