class TabulaException(Exception):
    pass


class TabulaAuthException(Exception):
    def __init__(self, count, error_type, *args, **kwargs):
        super(TabulaAuthException, self).__init__(*args, **kwargs)
        self.count = count
        self.error_type = error_type
