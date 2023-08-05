from functools import wraps

from rook.interface import Rook

def serverless_rook(f):
    @wraps(f)
    def handler(*args, **kwargs):
        from rook import auto_start
        ret = f(*args, **kwargs)
        Rook().flush()
        return ret

    return handler

try:
    from chalice import Chalice

    class RookoutChalice(Chalice):
        @serverless_rook
        def __call__(self, *args, **kwargs):
            return super(RookoutChalice, self).__call__(*args, **kwargs)


except ImportError:
    pass