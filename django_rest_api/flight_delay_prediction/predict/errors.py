class NoPreprocessObjectError:
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f'Error: {self.msg}'


class IncompleteModelInputError:
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f'Error: {self.msg}'
