from command_handler.request.exceptions import InvalidRequestException


class AssertionFailedException(InvalidRequestException, AssertionError):
    pass
