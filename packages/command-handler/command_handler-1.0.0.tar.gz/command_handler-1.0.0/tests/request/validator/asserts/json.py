from unittest import TestCase
from unittest.mock import MagicMock
from werkzeug.exceptions import BadRequest

from command_handler.request.validator.asserts import json
from command_handler.request.validator.exceptions import AssertionFailedException


class JsonRequestValidatorTest(TestCase):
    def testRaisesExceptionWhenRequestIsNotJson(self):
        request = MagicMock()
        request.is_json = False

        with self.assertRaises(AssertionFailedException) as cm:
            json(request)

        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(str(cm.exception), "Invalid `Content-Type` header")

    def testReturnsNoneWhenRequestIsJson(self):
        request = MagicMock()
        request.is_json = True

        self.assertIsNone(json(request))

    def testRaisesExceptionWhenRequestBodyIsNotJsonParseable(self):
        request = MagicMock()
        request.is_json = True
        request.get_json.side_effect = BadRequest()

        with self.assertRaises(AssertionFailedException) as cm:
            json(request)

        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(str(cm.exception), "Content is not JSON-parseable")
