"""
Data Service Exception
"""


class EntityNotFound(Exception):
    pass


class InvalidParameter(Exception):
    pass


class NotAuthorized(Exception):
    pass


class ServerError(Exception):
    pass