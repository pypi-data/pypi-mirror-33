import logging
from marshmallow.exceptions import ValidationError

from clientlib.functions import Function
from clientlib.exceptions import (
    ExecutionError, ResponseDeserializationError, PayloadSerializationError
)
from clientlib.models import EndpointResponse


logger = logging.getLogger(__name__)


class Endpoint(object):
    """Endpoint declaration class"""

    def __init__(self, method, endpoint, args=None, params=None, payload=None,
                 requires_auth=True, response_schema=None,
                 payload_schema=None):
        """Create a new Endpoint object

        :param str method: the http method to use
        :param str endpoint: the endpoint
        :param list[str] args: the endpoint address arguments
        :param list[str] params: the endpoint url arguments
        :param str payload: the endpoint payload
        :param boolean requires_auth: indicator flag that is used to specify
        if the endpoint requires authentication
        :param Schema response_schema: the expected response schema
        :param Schema payload_schema: the payload schema
        """
        self._method = method
        self._endpoint = endpoint
        self._args = args or []
        self._params = params or []
        self._payload = payload
        self._requires_auth = requires_auth
        self._response_schema = response_schema
        self._payload_schema = payload_schema

        self._function = None
        self._session = None

    def _initialize_function(self, obj):
        self._function = Function(
            session=self._session,
            base_url=obj.base_url,
            method=self._method,
            endpoint=self._endpoint,
            auth=obj.auth if self._requires_auth else None,
            timeout=obj.timeout,
            verify=obj.verify
        )

    def __get__(self, obj, obj_type):
        self._session = obj.session

        if self._function is None:
            self._initialize_function(obj)

        return self.execute

    def _can_serialize_payload(self, payload):
        return payload is not None and self._payload_schema is not None

    def _create_serialized_payload(self, payload):
        try:
            serialized_payload = self._payload_schema.dump(payload)
        except ValidationError as e:
            logger.exception("failed to serialize the endpoint payload")

            raise PayloadSerializationError(
                reason="failed to serialize the endpoint payload",
                payload=payload,
                errors=e.messages
            )

        if serialized_payload.errors:
            logger.error("errors exist in the serialized endpoint payload")

            raise PayloadSerializationError(
                reason="errors exist in the serialized endpoint payload",
                payload=payload,
                errors=serialized_payload.errors
            )

        return serialized_payload.data

    def _create_payload(self, kwargs):
        payload = kwargs[self._payload] if self._payload is not None else None

        if self._can_serialize_payload(payload):
            payload = self._create_serialized_payload(payload)

        return payload

    def _create_args(self, kwargs):
        return {
            arg: kwargs[arg]
            for arg in self._args
        }

    def _create_params(self, kwargs):
        return {
            param: kwargs[param]
            for param in self._params
            if param in kwargs
        }

    def _can_deserialize(self):
        return self._response_schema is not None

    def _deserialize_response(self, response):
        if not (200 <= response.status_code < 300):
            raise ExecutionError(
                reason="the request was not executed successfully",
                response=response
            )

        try:
            deserialized_response = self._response_schema.load(response.json)
        except ValidationError as e:
            logger.exception("failed to deserialize endpoint response")

            raise ResponseDeserializationError(
                reason="failed to deserialize endpoint response",
                response=response,
                errors=e.messages
            ) from e

        if deserialized_response.errors:
            logger.error("errors exist in deserialized endpoint response")

            raise ResponseDeserializationError(
                reason="errors exist in deserialized endpoint response",
                response=response,
                errors=deserialized_response.errors
            )

        return EndpointResponse(
            response=response,
            data=deserialized_response.data
        )

    def _create_endpoint_response(self, response):
        if self._can_deserialize():
            return self._deserialize_response(response)
        else:
            return response

    def execute(self, **kwargs):
        """Execute a request to the endpoint

        :param kwargs: the endpoint arguments. These are the items defined
        in the args and params arguments in the constructor
        :return: dict|EndpointResponse
        """
        args = self._create_args(kwargs)
        params = self._create_params(kwargs)
        payload = self._create_payload(kwargs)

        response = self._function.execute(
            args=args,
            params=params,
            json=payload
        )

        return self._create_endpoint_response(response)
