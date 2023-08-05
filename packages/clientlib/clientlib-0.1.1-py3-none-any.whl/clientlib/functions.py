from clientlib.requests import APIRequest


class Function(object):
    """API function object"""

    def __init__(self, session, base_url, method, endpoint, auth=None,
                 timeout=5, verify=True):
        """Create a new Function object

        :param Session session: the session to use
        :param str base_url: the api base url
        :param str method: the http method to use
        :param str endpoint: the endpoint path
        :param AuthBase auth: the authenticator object to use
        :param int timeout: the request timeout value
        :param boolean verify: flag that indicates whether to verify ssl
        """
        self.session = session
        self.base_url = base_url
        self.method = method
        self.endpoint = endpoint
        self.auth = auth
        self.timeout = timeout
        self.verify = verify

    def execute(self, args=None, params=None, json=None):
        """Execute the function

        :param dict args: the endpoint arguments
        :param dict params: the endpoint url parameters
        :param dict json: the payload
        :rtype: Response
        :return: the function execution result
        """
        request = APIRequest(
            session=self.session,
            base_url=self.base_url,
            method=self.method,
            endpoint=self.endpoint,
            args=args,
            params=params,
            json=json,
            auth=self.auth,
            timeout=self.timeout,
            verify=self.verify
        )

        return request.execute()
