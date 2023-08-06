from sys import modules
from unittest import TestCase
from unittest.mock import MagicMock, patch

from command_handler.command.handler.registry import Registry
from command_handler.request.validator.asserts.command import command
from command_handler.request.validator.exceptions import AssertionFailedException


class CommandRequestValidatorTest(TestCase):
    patchers = {}

    def setUp(self):
        self.patchers["storage"] = patch.object(
            target=modules["command_handler.request.validator.asserts.command"],
            attribute="registry",
            new_callable=Registry,
        )

        self.registry = self.patchers["storage"].start()

        self.registry.add("foo.bar.baz", lambda x: x, {})

    def tearDown(self):
        for name, patcher in self.patchers.items():
            patcher.stop()

    def testRaisesExceptionWhenRequestIsEmpty(self):
        request = MagicMock()

        with self.assertRaises(AssertionFailedException) as cm:
            command(request)

        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(str(cm.exception), "Either `payload` or `command` field is missing")

    def testRaisesExceptionWhenRequestContainsPayloadOnly(self):
        request = MagicMock()
        request.get_json.return_value = {
            "payload": {},
        }

        with self.assertRaises(AssertionFailedException) as cm:
            command(request)

        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(str(cm.exception), "Either `payload` or `command` field is missing")

    def testRaisesExceptionWhenRequestContainsCommandNameOnly(self):
        request = MagicMock()
        request.get_json.return_value = {
            "command": "foo.bar.baz",
        }

        with self.assertRaises(AssertionFailedException) as cm:
            command(request)

        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(str(cm.exception), "Either `payload` or `command` field is missing")

    def testReturnsNoneWhenRequestContainsBothPayloadAndCommandName(self):
        request = MagicMock()
        request.get_json.return_value = {
            "command": "foo.bar.baz",
            "payload": {},
        }

        self.assertIsNone(command(request))

    def testRaisesExceptionWhenPayloadIsNotADict(self):
        request = MagicMock()
        request.get_json.return_value = {
            "command": "foo.bar.baz",
            "payload": "foo",
        }

        with self.assertRaises(AssertionFailedException) as cm:
            command(request)

        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(str(cm.exception), "Field `payload` is not a dictionary")

    def testRaisesExceptionWhenCommandNameIsNotAString(self):
        request = MagicMock()
        request.get_json.return_value = {
            "command": [],
            "payload": {},
        }

        with self.assertRaises(AssertionFailedException) as cm:
            command(request)

        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(str(cm.exception), "Field `command` is not a string")

    def testRaisesExceptionWhenGivenCommandIsNotDefinedInCommandRegistry(self):
        request = MagicMock()
        request.get_json.return_value = {
            "command": "foo.bar",
            "payload": {},
        }

        with self.assertRaises(AssertionFailedException) as cm:
            command(request)

        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(str(cm.exception), "Value of field `command` is not valid command key")

    def testRaisesExceptionWhenGivenCommandDoesNotMatchSchema(self):
        self.registry.add("foo.bar", lambda x: x, {
            "type": "object",
            "properties": {
                "foo": {"type": "number"},
                "bar": {"type": "string"},
            },
            "required": [
                "foo",
                "bar",
            ],
        })

        request = MagicMock()
        request.get_json.return_value = {
            "command": "foo.bar",
            "payload": {},
        }

        with self.assertRaises(AssertionFailedException) as cm:
            command(request)

        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(str(cm.exception), "Value of field `payload` does not match schema of requested command")
