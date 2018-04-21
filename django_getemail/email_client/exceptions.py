class BaseEmailClientException(Exception):
    """Basic exception for errors raised by email client"""
    default_msg = "An email client error occurred."

    def __init__(self, msg=None):
        self.message = msg or self.default_msg


class ServiceError(BaseEmailClientException):
    pass


class EmailClientException(BaseEmailClientException):
    pass


class ReadOnlyEmailClientException(BaseEmailClientException):
    default_msg = "Read only allowed."


class AuthenticationFailedException(EmailClientException):
    default_msg = "Authentication failed: invalid credentials."


class BlockedSigningException(EmailClientException):
    default_msg = "Email client blocked signing into account."
