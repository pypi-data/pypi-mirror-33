from werkzeug.exceptions import BadRequest

from command_handler.request.validator.exceptions import AssertionFailedException


def json(request):
    try:
        assert request.is_json, "Invalid `Content-Type` header"

        request.get_json()
    except AssertionError as e:
        raise AssertionFailedException(str(e), 400) from e
    except BadRequest as e:
        raise AssertionFailedException("Content is not JSON-parseable", 400) from e
