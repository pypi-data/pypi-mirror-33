from requests.auth import AuthBase


class TokenAuthenticator(AuthBase):
    """Token bases authenticator

    This authenticator will add the token in the Authorization header of the
    request
    """

    def __init__(self, token, authentication_type=None):
        """Create a new TokenAuthenticator object

        :param str token: the token
        """
        self.token = token
        self.authentication_type = authentication_type

    def _create_authorization_value(self):
        if self.authentication_type is not None:
            return "{} {}".format(self.authentication_type, self.token)
        else:
            return self.token

    def __call__(self, request):
        request.headers["Authorization"] = self._create_authorization_value()

        return request
