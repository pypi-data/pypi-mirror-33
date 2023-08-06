"""
Request class.

Represents a JSON-RPC request object.
"""
from contextlib import contextmanager
import logging
import traceback

from .exceptions import JsonRpcServerError
from .log import log
from .request_utils import (
    convert_camel_case as ccc,
    convert_camel_case_keys as ccc_keys,
    validate_against_schema,
    validate_arguments_against_signature,
    get_method,
    get_arguments,
)
from .response import Response, RequestResponse, NotificationResponse, ExceptionResponse


logger = logging.getLogger(__name__)


class Request(object):
    """
    Represents a JSON-RPC Request object.

    Encapsulates a JSON-RPC request, providing details such as the method name,
    arguments, and whether it's a request or a notification, and provides a
    ``process`` method to execute the request.
    """

    @contextmanager
    def handle_exceptions(self):
        """Sets the response value"""
        try:
            yield
        except Exception as exc:
            # Log the exception if it wasn't explicitly raised by the method
            if not isinstance(exc, JsonRpcServerError):
                log(logger, logging.ERROR, traceback.format_exc())
            # Notifications should not be responded to, even for errors (unless
            # overridden in configuration)
            if self.is_notification and not self.notification_errors:
                self.response = NotificationResponse()
            else:
                self.response = ExceptionResponse(
                    exc, getattr(self, "request_id", None), debug=self.debug
                )

    def __init__(
        self,
        request,
        context=None,
        convert_camel_case=False,
        debug=False,
        schema_validation=True,
        notification_errors=False,
    ):
        """
        :param request: JSON-RPC request, in dict form.
        :param context: Optional context object that will be passed to the RPC
            method.
        :param convert_camel_case:
        :param debug:
        :param notification_errors:
        :param schema_validation:
        """
        self.debug = debug
        self.notification_errors = notification_errors
        # Handle parsing & validation errors
        with self.handle_exceptions():
            # Validate against the JSON-RPC schema
            if schema_validation:
                validate_against_schema(request)
            # Get method name from the request. We can assume the key exists
            # because the request passed the schema.
            self.method_name = request["method"]
            # Get arguments from the request, if any
            self.args, self.kwargs = get_arguments(
                request.get("params"), context=context
            )
            # Get request id, if any
            self.request_id = request.get("id")
            # Convert camelcase to snake case
            if convert_camel_case:
                self.method_name = ccc(self.method_name)
                if self.kwargs:
                    self.kwargs = ccc_keys(self.kwargs)
            self.response = None

    @property
    def is_notification(self):
        """
        Returns True if the request is a JSON-RPC Notification (ie. No id
        attribute is included). False if it's a request.
        """
        return hasattr(self, "request_id") and self.request_id is None

    def call(self, methods):
        """
        Call the appropriate method from a list.

        Find the method from the passed list, and call it, returning a Response
        """
        # Validation or parsing may have failed in __init__, in which case
        # there's no point calling. It would've already set the response.
        if not self.response:
            # Handle setting the result/exception of the call
            with self.handle_exceptions():
                # Get the method object from a list (raises MethodNotFound)
                callable_ = self.get_method(methods)
                # Ensure the arguments match the method's signature
                validate_arguments_against_signature(callable_, self.args, self.kwargs)
                # Call the method
                result = callable_(*(self.args or []), **(self.kwargs or {}))
                # Set the response
                if self.is_notification:
                    self.response = NotificationResponse()
                else:
                    self.response = RequestResponse(self.request_id, result)
        # Ensure the response has been set before returning it
        assert isinstance(self.response, Response), "Invalid response type"
        return self.response

    def get_method(self, methods):
        """
        Find and return a callable representing the method for this request.

        :param methods: List or dictionary of named functions
        :raises MethodNotFound: If no method is found
        :returns: Callable representing the method
        """
        return get_method(methods, self.method_name)
