"""
HTTP API specific exceptions and responses.
"""

from pyramid.httpexceptions import HTTPException
from pyramid.response import Response

from ichnaea.exceptions import BaseClientError, BaseServiceError


class JSONException(HTTPException):
    """
    A base class for HTTP responses acting as exceptions and containing
    a JSON body.
    """

    code = 500
    empty_body = False
    message = ""

    def __init__(self):
        # explicitly avoid calling the HTTPException init magic
        if not self.empty_body:
            Response.__init__(self, status=self.code, json_body=self.json_body())
        else:
            Response.__init__(self, status=self.code)
        Exception.__init__(self)
        self.detail = self.message

        if self.empty_body:
            del self.content_type
            del self.content_length

    def __str__(self):
        return "<%s>: %s" % (self.__class__.__name__, self.code)

    def json_body(self):
        """A JSON representation of this response."""
        return {}


class UploadSuccess(JSONException):
    """
    A successful upload response.
    """

    code = 200


class UploadSuccessV0(UploadSuccess):
    """
    A variant of :exc:`~ichnaea.api.exceptions.UploadSuccess` used
    in earlier version 0 HTTP APIs.
    """

    code = 204
    empty_body = True


class BaseAPIError(JSONException):
    """
    A base class representing API errors that all act as HTTP responses
    and have a similar JSON body.
    """

    code = 400
    domain = ""
    reason = ""
    message = ""

    def json_body(self):
        """A JSON representation of this response."""
        return {
            "error": {
                "errors": [
                    {
                        "domain": self.domain,
                        "reason": self.reason,
                        "message": self.message,
                    }
                ],
                "code": self.code,
                "message": self.message,
            }
        }


class BaseAPIClientError(BaseAPIError, BaseClientError):
    """
    A base class for all errors that are the client's fault.
    """

    code = 400
    domain = "global"
    reason = "badRequest"
    message = "Bad Request"


class BaseAPIServiceError(BaseAPIError, BaseServiceError):
    """
    A base class for all errors that are the service's fault.
    """

    code = 500
    domain = "global"
    reason = "internalError"
    message = "Internal Error"


class Forbidden(BaseAPIClientError):
    """
    Static response for 401 status codes
    """

    code = 403
    domain = "global"
    reason = "Forbidden"
    message = "Forbidden"


class DailyLimitExceeded(BaseAPIClientError):
    """
    Response given when daily quota was exceeded.
    """

    code = 403
    domain = "usageLimits"
    reason = "dailyLimitExceeded"
    message = "You have exceeded your daily limit."


class InvalidAPIKey(BaseAPIClientError):
    """
    Response for missing or invalid API keys.
    """

    code = 400
    domain = "usageLimits"
    reason = "keyInvalid"
    message = "Missing or invalid API key."


class LocationNotFound(BaseAPIClientError):
    """
    Response given when mo location could be found.
    """

    code = 404
    domain = "geolocation"
    reason = "notFound"
    message = "Not found"


class ParseError(BaseAPIClientError):
    """
    Response given when the request couldn't be parsed.
    """

    code = 400
    domain = "global"
    reason = "parseError"
    message = "Parse Error"
    error_details = None

    def __init__(self, details=None):
        self.error_details = details
        super().__init__()

    def json_body(self):
        content = super().json_body()
        if self.error_details:
            content["details"] = self.error_details
        return content


class ServiceUnavailable(BaseAPIServiceError):
    """
    Response given when the service is (partially) unavailable.
    """

    code = 503
    domain = "global"
    reason = "serviceUnavailable"
    message = "Service Unavailable"
