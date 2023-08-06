from sys import modules
from unittest import TestCase
from unittest.mock import call, MagicMock, Mock, patch

from command_handler import CommandHandler


class CommandHandlerTest(TestCase):
    def testCommandHandlerReturnsInstanceOfCommandHandler(self):
        app = MagicMock()

        self.assertIsInstance(CommandHandler(app), CommandHandler)

    def testInitCallsAddUrlRuleOnGivenApplication(self):
        app = MagicMock()
        CommandHandler(app)

        app.add_url_rule.assert_called()

    def testInitCallsAddUrlRuleOnGivenApplicationWithUrl(self):
        app = MagicMock()
        CommandHandler(app)

        args, kwargs = app.add_url_rule.call_args
        assert "rule" in kwargs or len(args) >= 1

        url = kwargs.get("rule") if "rule" in kwargs else args[0]
        self.assertEqual(url, "/command")

    def testInitCallsAddUrlRuleOnGivenApplicationWithPrefixedUrl(self):
        app = MagicMock()
        CommandHandler(app, rulePrefix="/foo")

        args, kwargs = app.add_url_rule.call_args
        url = kwargs.get("rule") if "rule" in kwargs else args[0]
        self.assertEqual(url, "/foo/command")

    def testInitCallsAddUrlRuleOnGivenApplicationWithViewFunc(self):
        app = MagicMock()

        CommandHandler(app)

        args, kwargs = app.add_url_rule.call_args
        assert "view_func" in kwargs or len(args) >= 3

        view_func = kwargs.get("view_func") if "view_func" in kwargs else args[2]
        with patch("command_handler.views.Invoker.dispatch_request") as dispatcher:
            view_func()

            dispatcher.assert_called()

    def testInitCallsAddUrlRuleOnGivenApplicationWithPostAsOnlyAllowedMethod(self):
        app = MagicMock()
        CommandHandler(app)

        args, kwargs = app.add_url_rule.call_args
        assert "methods" in kwargs

        methods = kwargs.get("methods")
        self.assertIsInstance(methods, list)
        self.assertEqual(len(methods), 1)
        assert "POST" in methods

    def testInitPassesValidatorParamToInvokerInitializer(self):
        app = MagicMock()
        validators = ["foo", "bar"]

        CommandHandler(app, validators=validators)

        args, kwargs = app.add_url_rule.call_args
        view_func = kwargs.get("view_func") if "view_func" in kwargs else args[2]
        with patch("command_handler.views.Invoker.dispatch_request"):
            with patch.object(view_func, "view_class", Mock("command_handler.views.Invoker")) as view_class:
                view_func()

                args, kwargs = view_class.call_args
                assert "validators" in kwargs
                self.assertListEqual(kwargs["validators"], validators)

    def testAddHandlerWrappsGivenMethodWithHandlerClassAndAddsItToTheRegistry(self):
        def handler():
            pass

        def handlerDecorator():
            return handler()

        ch = CommandHandler(MagicMock())
        extras = {
            "transformer": lambda x: x,
            "postProcessor": lambda x: None,
        }

        with patch.object(modules["command_handler.handler"], "Handler") as Handler:
            Handler.return_value = handlerDecorator
            with patch.object(modules["command_handler.handler"], "registry") as registry:
                ch.addHandler(handler, "foo.bar", {}, **extras)

        Handler.assert_called()
        Handler.assert_has_calls([call(handler,  **extras)])

        registry.add.assert_called()
        registry.add.assert_has_calls([call("foo.bar", handlerDecorator, {})])
