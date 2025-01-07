

class Response:
    def __init__(self, res, err_msg):
        self.res = res
        self.err = err_msg

    def __bool__(self):
        return self.res

RESPONSE_OK = Response(True, "")

def RESPONSE_ERR(err_msg):
    return Response(False, err_msg)

# wrapper func
def default_response_ok(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        return RESPONSE_OK
    return inner
