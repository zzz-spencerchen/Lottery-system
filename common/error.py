

class NotPathError(Exception):
    def __init__(self, message):
        self.message = message


class FormatError(Exception):
    def __init__(self, message='need json format'):
        self.message = message


class NotFileError(Exception):
    def __init__(self, message='this is not a file'):
        self.message = message


class UserExistsError(Exception):
    def __init__(self, message):
        self.message = message


class RuleError(Exception):
    def __init__(self, message):
        self.message = message


class LevelError(Exception):
    def __init__(self, message):
        self.message = message


class NegativeNumberError(Exception):
    def __init__(self, message):
        self.message = message


class NotUserError(Exception):
    def __init__(self, message):
        self.message = message


class UserActiceError(Exception):
    def __init__(self, message):
        self.message = message
