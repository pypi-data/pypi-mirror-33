import logging

from requests import Request
from requests.exceptions import RequestException, Timeout

from clientlib.models import Response
from clientlib.exceptions import (
    InvalidResponseContentType, EndpointTimeout, EndpointRequestError
)


logger = logging.getLogger(__name__)


class APIRequest(object):
    """API request object"""

    def __init__(self, session, base_url, method, endpoint, args=None,
                 params=None, json=None, auth=None, timeout=5, verify=True):
        """Create a new APIRequest object

        :param Session session: the session object to use for the requests
        :param str base_url: the api base url
        :param str method: the http method to use
        :param str endpoint: the endpoint path
        :param dict args: the request arguments
        :param dict params: the request url parameters
        :param dict json: the request payload
        :param AuthBase auth: the authenticator object to use
        :param int timeout: the request timeout
        :param boolean verify: flag that indicated whether to verify ssl
        """
        self.session = session
        self.base_url = base_url
        self.method = method
        self.endpoint = endpoint
        self.args = args
        self.params = params
        self.json = json
        self.auth = auth
        self.timeout = timeout
        self.verify = verify

    def _create_endpoint(self):
        if self.args is None:
            return self.endpoint
        else:
            return self.endpoint.format(**self.args)

    def _create_url(self):
        return "{base_url}{endpoint}".format(
            base_url=self.base_url,
            endpoint=self._create_endpoint()
        )

    def _create_request(self):
        return Request(
            method=self.method,
            url=self._create_url(),
            params=self.params,
            json=self.json,
            auth=self.auth
        )

    def _send_request(self):
        request = self._create_request()
        prepared_request = request.prepare()

        with self.session:
            return self.session.send(
                request=prepared_request,
                verify=self.verify,
                timeout=self.timeout
            )

    def _extract_data(self, response):
        try:
            return response.json()
        except (ValueError, TypeError) as e:
            logger.exception("failed to convert response content to json")

            raise InvalidResponseContentType(
                status_code=response.status_code,
                content=response.text
            ) from e

    def execute(self):
        """Execute the api request

        :rtype: Response
        :return: the request result
        """
        try:
            response = self._send_request()
        except Timeout as e:
            logger.error("a timeout occurred while executing request")

            raise EndpointTimeout(
                reason="a timeout occurred while executing request",
                base_url=self.base_url,
                method=self.method,
                endpoint=self.endpoint
            ) from e
        except RequestException as e:
            logger.exception("an error occurred while executing request")

            raise EndpointRequestError(
                reason="an error occurred while executing request",
                base_url=self.base_url,
                method=self.method,
                endpoint=self.endpoint
            ) from e

        json = self._extract_data(response)

        return Response(
            status_code=response.status_code,
            headers=response.headers,
            json=json
        )
