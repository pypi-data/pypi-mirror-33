from flask.views import View
from json import dumps, loads
from unittest import TestCase
from unittest.mock import call, Mock, patch

from command_handler.request.exceptions import InvalidRequestException
from command_handler.command.handler.registry import Registry
from command_handler.request.validator.exceptions import AssertionFailedException
from command_handler.views import Invoker


class InvokerTest(TestCase):
    patchers = {}

    def setUp(self):
        self.patchers["command.storage"] = patch("command_handler.views.registry", new_callable=Registry)
        self.patchers["validator.factory"] = patch("command_handler.views.ValidatorFactory")

        self.commandRegistry = self.patchers["command.storage"].start()
        self.validatorFactory = self.patchers["validator.factory"].start()

        self.commandRegistry.add("foo", lambda x, y: None, {})

    def tearDown(self):
        for name, patcher in self.patchers.items():
            patcher.stop()

    def __init__(self, methodName):
        TestCase.__init__(self, methodName)

        from flask import Flask

        self.app = Flask(__name__)
        self.app.config["TESTING"] = True

    def testInvokerReturnsInstanceOfInvoker(self):
        self.assertIsInstance(Invoker(), Invoker)

    def testInvokerObjectIsInstanceOfFlaskView(self):
        self.assertIsInstance(Invoker(), View)

    def testInitAddsRequiredValidatorsWhenMissing(self):
        Invoker(validators=["foo"])

        self.validatorFactory.create.assert_called()
        args, kwargs = self.validatorFactory.create.call_args

        types = kwargs["types"] if "types" in kwargs else args[0]
        self.assertIn("command", types)
        self.assertIn("json", types)
        self.assertIn("foo", types)

    def testInitDoesNotDoublesRequiredValidatorsWhenAlreadyDefined(self):
        Invoker(validators=["command", "json"])

        self.validatorFactory.create.has_calls(call(["command", "json"]))

    def testDispatchRequestRaisesErrorWhenRequestMethodIsGet(self):
        with self.app.test_request_context(method="GET"):
            with self.assertRaises(AssertionError):
                Invoker().dispatch_request()

    def testDispatchRequestRaisesErrorWhenRequestMethodIsPut(self):
        with self.app.test_request_context(method="PUT"):
            with self.assertRaises(AssertionError):
                Invoker().dispatch_request()

    def testDispatchRequestRaisesErrorWhenRequestMethodIsDelete(self):
        with self.app.test_request_context(method="DELETE"):
            with self.assertRaises(AssertionError):
                Invoker().dispatch_request()

    def testDispatchRequestReturnsTupleWhenRequestMethodIsPost(self):
        with self.app.test_request_context(
            content_type="application/json",
            data=dumps({"command": "foo", "payload": {}}),
            method="POST",
        ):
            response = Invoker().dispatch_request()

        self.assertIsInstance(response, tuple)
        self.assertEqual(len(response), 3)

    def testDispatchRequestReturnsJsonContentTypeHeader(self):
        with self.app.test_request_context(
            content_type="application/json",
            data=dumps({"command": "foo", "payload": {}}),
            method="POST",
        ):
            response = Invoker().dispatch_request()

        self.assertIn("Content-type", response[2])
        self.assertEqual(response[2]["Content-type"], "application/json")

    def testDispatchRequestTestsRequestWithValidatorReturnedByValidatorFactory(self):
        controller = Invoker()

        with self.app.test_request_context(
            content_type="application/json",
            data=dumps({"command": "foo", "payload": {}}),
            method="POST",
        ):
            controller.dispatch_request()

        self.validatorFactory.create().test.assert_called()

    def testDispatchRequestReturnsResponseCodeSameAsCodeOfExceptionRaisedByValidator(self):
        self.validatorFactory.create().test.side_effect = AssertionFailedException(code=1237)

        with self.app.test_request_context(
            content_type="application/json",
            data=dumps({"command": "foo", "payload": {}}),
            method="POST",
        ):
            response = Invoker().dispatch_request()

        self.assertEqual(response[1], 1237)

    def testDispatchRequestReturnsJsonResponseWithMessageFromExceptionRaisedByValidator(self):
        self.validatorFactory.create().test.side_effect = AssertionFailedException("Foo Bar")

        with self.app.test_request_context(
            content_type="application/json",
            data=dumps({"command": "foo", "payload": {}}),
            method="POST",
        ):
            response = Invoker().dispatch_request()

        body = loads(response[0])
        self.assertIn("error", body)
        self.assertEqual(body["error"], "Foo Bar")

    def testDispatchRequestReturnsResponseCodeSameAsCodeOfExceptionRaisedByHandler(self):
        handler = Mock()
        handler.side_effect = InvalidRequestException(code=123)

        self.commandRegistry.add("foo.bar", handler, {})

        with self.app.test_request_context(
            content_type="application/json",
            data=dumps({"command": "foo.bar", "payload": {}}),
            method="POST",
        ):
            response = Invoker().dispatch_request()

        self.assertEqual(response[1], 123)

    def testDispatchRequestReturnsJsonResponseWithMessageFromExceptionRaisedByHandler(self):
        handler = Mock()
        handler.side_effect = InvalidRequestException("Foo")

        self.commandRegistry.add("foo.bar", handler, {})

        with self.app.test_request_context(
            content_type="application/json",
            data=dumps({"command": "foo.bar", "payload": {}}),
            method="POST",
        ):
            response = Invoker().dispatch_request()

        body = loads(response[0])
        self.assertIn("error", body)
        self.assertEqual(body["error"], "Foo")

    def testDispatchRequestReturnsResponseWithCode500WhenHandlerIsRaisingException(self):
        handler = Mock()
        handler.side_effect = Exception

        self.commandRegistry.add("foo.bar", handler, {})

        with self.app.test_request_context(
            content_type="application/json",
            data=dumps({"command": "foo.bar", "payload": {}}),
            method="POST",
        ):
            response = Invoker().dispatch_request()

        self.assertEqual(response[1], 500)

    def testDispatchRequestCallsHandlerForGivenCommandWithPayloadiAndCommandName(self):
        command = "foo.bar.baz"
        payload = {
            "foo": ["bar", "baz"]
        }
        schema = {
            "type": "object",
            "properties": {
                "foo": {
                    "type": "array",
                    "minItems": 1,
                    "enum": [
                        "bar",
                        "baz",
                    ],
                },
            },
            "required": ["foo"]
        }

        handler = Mock()
        self.commandRegistry.add(command, handler, schema)

        with self.app.test_request_context(
            content_type="application/json",
            data=dumps({
                "payload": payload,
                "command": command,
            }),
            method="POST",
        ):
            response = Invoker().dispatch_request()

        self.assertEqual(handler.call_count, 1)
        handler.assert_has_calls([call(payload, command)])
