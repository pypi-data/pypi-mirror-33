from unittest import TestCase

from command_handler.request.exceptions import InvalidRequestException
from command_handler.request.validator.exceptions import AssertionFailedException


class AssertionFailedExceptionTest(TestCase):
    def testIsInstanceOfAssertionError(self):
        self.assertIsInstance(AssertionFailedException(), Exception)

    def testIsInstanceOfInvalidRequestException(self):
        self.assertIsInstance(AssertionFailedException(), InvalidRequestException)

    def testStringifiedReturnsMessageGivenAsInitParam(self):
        exception = AssertionFailedException("Foo Bar Message")

        self.assertEqual(str(exception), "Foo Bar Message")

    def testCodeAttributeIsEqualToCodeGivenAsInitParam(self):
        exception = AssertionFailedException(code=999)

        self.assertEqual(exception.code, 999)

    def testCodeAttributesIsEqualTo400IfNoCodeGiven(self):
        exception = AssertionFailedException()

        self.assertEqual(exception.code, 400)
