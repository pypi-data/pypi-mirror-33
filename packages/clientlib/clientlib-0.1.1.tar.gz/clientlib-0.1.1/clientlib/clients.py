from abc import ABCMeta

from requests import Session


class Client(metaclass=ABCMeta):
    """Client base class"""

    def __init__(self, base_url, auth=None, timeout=5, verify=True):
        """Create a new Client object

        :param str base_url: the APi base url
        :param AuthBase auth: the authenticator object
        :param int timeout: the request timeout
        :param boolean verify: flag that indicates whether to verify ssl or not
        """
        self.base_url = base_url
        self.auth = auth
        self.timeout = timeout
        self.verify = verify

        self.session = Session()
