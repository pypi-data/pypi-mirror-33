class FilterException(Exception):
    pass


class FilterWrongArguments(FilterException):
    pass


class FilterDoesNotExist(FilterException):
    pass


class RepositoryException(Exception):
    pass


class RepositoryDoesNotExistException(Exception):
    pass


class AuthException(Exception):
    pass
