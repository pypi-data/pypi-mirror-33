from collections import namedtuple

Response = namedtuple("Response", ["status_code", "headers", "json"])
EndpointResponse = namedtuple("EndpointResponse", ["response", "data"])
