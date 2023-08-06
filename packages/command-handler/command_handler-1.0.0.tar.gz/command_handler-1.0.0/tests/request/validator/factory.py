from unittest import TestCase
from unittest.mock import patch

from command_handler.request.validator import ValidatorFactory
from command_handler.request.validator.asserts import command, json, privateIp
from command_handler.request.validator.validator import Validator


class ValidatorFactoryTest(TestCase):
    def testCreateReturnsValidatorObject(self):
        validator = ValidatorFactory.create([])

        self.assertIsInstance(validator, Validator)

    def testCreateReturnsValidatorObjectWithMatchingPredefinedAsserts(self):
        with patch("command_handler.request.validator.factory.Validator") as ValidatorPatch:
            validator = ValidatorFactory.create([
                "command",
                "json",
                "privateIp",
            ])

        args, kwargs = ValidatorPatch.call_args
        asserts = kwargs.get("asserts") if "asserts" in kwargs else args[0]

        self.assertIn(command, asserts)
        self.assertIn(json, asserts)
        self.assertIn(privateIp, asserts)
