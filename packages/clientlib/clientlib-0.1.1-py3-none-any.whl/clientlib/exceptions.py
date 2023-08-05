class ClientlibException(Exception):
    def __init__(self, reason=None, *args):
        super(ClientlibException, self).__init__(reason, *args)

        self.reason = reason


class EndpointError(ClientlibException):
    pass


class EndpointResponseError(EndpointError):
    def __init__(self, reason=None, response=None, *args):
        super(EndpointResponseError, self).__init__(reason, response, *args)

        self.response = response


class ExecutionError(EndpointResponseError):
    pass


class ResponseDeserializationError(EndpointResponseError):
    def __init__(self, reason=None, response=None, errors=None, *args):
        super(ResponseDeserializationError, self).__init__(
            reason, response, errors, *args)

        self.errors = errors


class PayloadSerializationError(EndpointError):
    def __init__(self, reason=None, payload=None, errors=None, *args):
        super(PayloadSerializationError, self).__init__(
            reason, payload, errors, *args)

        self.payload = payload
        self.errors = errors


class InvalidResponseContentType(EndpointError):
    def __init__(self, status_code=None, content=None):
        super(InvalidResponseContentType, self).__init__(
            reason="the response content is not json"
        )

        self.status_code = status_code
        self.content = content


class RequestExecutionError(EndpointError):
    def __init__(self, reason=None, base_url=None, method=None, endpoint=None):
        super(RequestExecutionError, self).__init__(reason)

        self.base_url = base_url
        self.method = method
        self.endpoint = endpoint


class EndpointTimeout(RequestExecutionError):
    pass


class EndpointRequestError(RequestExecutionError):
    pass
