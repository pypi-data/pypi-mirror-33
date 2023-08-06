from flask import request
from flask.views import MethodView
from json import dumps

from command_handler.request.exceptions import InvalidRequestException
from command_handler.command.handler import registry
from command_handler.request.validator import ValidatorFactory


class Invoker(MethodView):
    def __init__(self, **kwargs):
        asserts = kwargs.get("validators", [])
        for a in ["command", "json"]:
            if a not in asserts:
                asserts.append(a)

        self.validator = ValidatorFactory.create(asserts)

    def post(self, *args, **kwargs):
        response = {}
        code = 202
        headers = {
            "Content-type": "application/json"
        }

        try:
            self.validator.test(request)

            # it is already validated by `command` and `json` asserts
            data = request.get_json()
            command = data["command"]
            handler = registry[command][0]

            payload = data["payload"]
            command = data["command"]

            handler(payload, command)
        except InvalidRequestException as e:
            code = e.code
            response["error"] = str(e)
        except BaseException:
            code = 500
            response["error"] = "Internal server error"

        return dumps(response), code, headers
