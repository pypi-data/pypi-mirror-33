
class ZcyBaseException(Exception):

    def __init__(self, msg):
        self.msg = msg


class ZcyNoMatchedEnvException(ZcyBaseException):
    pass


class ZcyAmbiguousEnvException(ZcyBaseException):
    pass


class ZcyNoMethodFoundException(ZcyBaseException):
    pass


class ZcyNoProviderVersionFoundException(ZcyBaseException):
    pass
