from unittest import TestCase

from command_handler.command.handler.exceptions import HandlerAlreadyExistsException


class HandlerAlreadyExistsExceptionTest(TestCase):
    def testIsInstanceOfValueError(self):
        self.assertIsInstance(HandlerAlreadyExistsException(), ValueError)
