from .validator import Validator


class ValidatorFactory():
    @staticmethod
    def create(types):
        asserts = [getattr(
            __import__(
                name="command_handler.request.validator.asserts",
                fromlist=[type],
            ),
            type,
        ) for type in types]

        return Validator(asserts)
