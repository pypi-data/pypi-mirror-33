from unittest import TestCase

from command_handler.request.exceptions import InvalidRequestException


class InvalidRequestExceptionTest(TestCase):
    def testIsInstanceOfException(self):
        self.assertIsInstance(InvalidRequestException(), Exception)

    def testStringifiedReturnsMessageGivenAsInitParam(self):
        exception = InvalidRequestException("Foo Bar Message")

        self.assertEqual(str(exception), "Foo Bar Message")

    def testCodeAttributeIsEqualToCodeGivenAsInitParam(self):
        exception = InvalidRequestException(code=999)

        self.assertEqual(exception.code, 999)

    def testCodeAttributesIsEqualTo400IfNoCodeGiven(self):
        exception = InvalidRequestException()

        self.assertEqual(exception.code, 400)
