from jsonschema import validate
from jsonschema.exceptions import ValidationError

from command_handler.command.handler import registry
from command_handler.request.validator.exceptions import AssertionFailedException


def command(request):
    body = request.get_json()
    try:
        assert all(k in body for k in ("payload", "command")), "Either `payload` or `command` field is missing"
        assert isinstance(body["command"], str), "Field `command` is not a string"
        assert isinstance(body["payload"], dict), "Field `payload` is not a dictionary"
        assert body["command"] in registry, "Value of field `command` is not valid command key"

        validate(body["payload"], registry[body["command"]][1])
    except AssertionError as e:
        raise AssertionFailedException(str(e), 400) from e
    except ValidationError as e:
        raise AssertionFailedException(
            message="Value of field `payload` does not match schema of requested command",
            code=400,
        ) from e
