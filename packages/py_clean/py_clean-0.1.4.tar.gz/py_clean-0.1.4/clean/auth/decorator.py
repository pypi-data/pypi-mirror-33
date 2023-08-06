from clean.exceptions import AuthException
from clean.auth.abs import DecodeToken


def create_decorator(v_class, token_finder, debug=False):
    def protect(scopes_check=None):
        def wrap(f):
            def wrapped_f(*args, **kwargs):
                if debug:
                    return f(*args, **kwargs)
                context = token_finder()
                dt = v_class(raw_token=context, scopes_check=scopes_check)
                try:
                    dt.is_valid()
                    kwargs['user_token'] = dt.user_token
                    return f(*args, **kwargs)
                except AuthException as e:
                    return dt.create_resp_err(str(e))
            return wrapped_f
        return wrap
    return protect


class DecoratorBuilder:

    def __init__(self, verify_class, token_finder_func):
        self.verify_class = verify_class
        self.token_finder_func = token_finder_func

        self.verify_decode_class()
        self.verify_token_finder()

    def verify_decode_class(self):
        if not issubclass(self.verify_class, DecodeToken):
            raise AttributeError('verify_class is not subclass of "DecodeToken"')

    def verify_token_finder(self):
        if not callable(self.token_finder_func):
            raise AttributeError('token_finder_func is not callable')

    def create(self):
        return create_decorator(self.verify_class, self.token_finder_func)
