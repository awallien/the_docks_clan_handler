

class Response:
    def __init__(self, res, err_msg):
        self.res = res
        self.err = err_msg

    def __bool__(self):
        return self.res

RESPONSE_OK = Response(True, "")
RESPONSE_ERR = lambda err_msg: Response(False, err_msg)

def default_response_ok(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        return RESPONSE_OK
    return inner


def raise_err_if_null(obj, obj_str):
    if obj is None:
        raise ValueError(f"{obj_str} is None")
