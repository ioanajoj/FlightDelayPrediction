class NoPreprocessObjectError:
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f'NoPreprocessObjectError: {self.msg}'


class IncompleteModelInputError:
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f'IncompleteModelInputError: {self.msg}'


class UnknownCategoryError(Exception):
    def __init__(self, message, errors):
        super(UnknownCategoryError, self).__init__(message)
        self.errors = errors


class RequestsExceeded(Exception):
    pass
