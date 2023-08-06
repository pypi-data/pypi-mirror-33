from unittest import TestCase
from unittest.mock import Mock

from command_handler.request.validator.validator import Validator


class ValidatorTest(TestCase):
    def testTestCallsEachAssertPassedToInitWithGivenRequest(self):
        asserts = [
            Mock(),
            Mock(),
            Mock(),
            Mock(),
        ]

        request = Mock()

        Validator(asserts).test(request)
        for a in asserts:
            a.assert_called()
            args, kwargs = a.call_args
            self.assertEqual(request, args[0])
