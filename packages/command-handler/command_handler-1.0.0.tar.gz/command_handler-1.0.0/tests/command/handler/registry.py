from unittest import TestCase

from command_handler.command.handler.exceptions import HandlerAlreadyExistsException
from command_handler.command.handler.registry import Registry


class RegistryTest(TestCase):
    def testDictTypeGetterReturnsDefinedHandlerAsATuple(self):
        def handler():
            pass

        schema = {}

        registry = Registry()
        registry.add("foo.bar", handler, schema)

        value = registry["foo.bar"]

        self.assertIsInstance(value, tuple)
        self.assertEqual(len(value), 2)
        self.assertEqual(value[0], handler)
        self.assertDictEqual(value[1], schema)

    def testDictTypeGetterReturnsHandlerWithMatchingKey(self):
        registry = Registry()
        registry.add("foo.*", lambda x: None, {})
        registry["foo.bar"]

    def testInTestReturnsFalseWhenNoHandlerHasBeenAdded(self):
        self.assertFalse("foo.bar" in Registry())

    def testInTestReturnsTrueWhenHandlerHasBeenAdded(self):
        registry = Registry()
        registry.add("foo.bar", lambda x: x, {})
        self.assertTrue("foo.bar" in registry)

    def testInTestReturnsTrueWhenMatchingHandlerWithHashHasBeenAdded(self):
        registry = Registry()
        registry.add("foo.#.bar", lambda x: None, {})
        self.assertTrue("foo.bar.baz.bar" in registry)

    def testInTestReturnsTrueWhenMatchingHandlerWithAsteriskHasBeenAdded(self):
        registry = Registry()
        registry.add("foo.*.baz", lambda x: None, {})
        self.assertTrue("foo.bar.baz" in registry)

    def testInTestReturnsFalseWhenTryingToMatchMoreThanOnePartIntoAsterisk(self):
        registry = Registry()
        registry.add("foo.*.baz", lambda x: None, {})
        self.assertFalse("foo.bar.bar.baz" in registry)

    def testInTestReturnsFalseWhenTryingToMatchEmptyStringIntoAsterisk(self):
        registry = Registry()
        registry.add("foo.*", lambda x: None, {})
        self.assertFalse("foo." in registry)

    def testInTestReturnsTrueWhenTryingToMatchNoWordStringIntoHash(self):
        registry = Registry()
        registry.add("foo.#", lambda x: None, {})
        self.assertTrue("foo" in registry)

    def testInTestReturnsFalseWhenTryingToMatchExtendedStringIntoHash(self):
        registry = Registry()
        registry.add("foo.#", lambda x: None, {})
        self.assertFalse("foo_bar" in registry)

    def testAddRaisesAnHandlerAlreadyExistsExceptionWhenMatchForGivenCommandAlreadyExists(self):
        registry = Registry()
        registry.add("foo.#", lambda x: None, {})

        with self.assertRaises(HandlerAlreadyExistsException):
            registry.add("foo.bar", lambda x: None, {})
