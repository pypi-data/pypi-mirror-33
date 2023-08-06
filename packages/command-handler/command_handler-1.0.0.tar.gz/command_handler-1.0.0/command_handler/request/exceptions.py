class InvalidRequestException(Exception):
    def __init__(self, message="", code=400):
        super().__init__(message)

        self.code = code
