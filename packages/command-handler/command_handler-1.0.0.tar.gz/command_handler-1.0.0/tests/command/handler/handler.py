from unittest import TestCase
from unittest.mock import call, MagicMock, Mock

from command_handler.command.handler import Handler


class HandlerTest(TestCase):
    def testHandlerInstanceIsInvokable(self):
        handler = Handler(lambda x, y: None)

        handler({}, "foo.bar")

    def testHandlerInvokeCallsGivenMethodWithParamsPassed(self):
        innerHandler = Mock()
        payload = {"foo": ["bar", "baz"]}

        handler = Handler(innerHandler)
        handler(payload, "foo.bar")

        innerHandler.assert_called()
        innerHandler.assert_has_calls([call(payload, "foo.bar")])

    def testHandlerInvokeCallsGivenMethodWithTransformedDataWhenTransformerPassed(self):
        innerHandler = Mock()
        params = {"foo": ["bar", "baz"]}

        handler = Handler(innerHandler, transformer=lambda x: [x, [x]])
        handler(params, "foo.bar")

        args, kwargs = innerHandler.call_args
        data = kwargs["data"] if "data" in kwargs else args[0]

        self.assertEqual(data, [params, [params]])

    def testHandlerInvokeCallsPostProcessorWithParamsPassedWhenPostProcessorGiven(self):
        manager = MagicMock()
        payload = {"foo": ["bar", "baz"]}
        command = "foo.bar"

        handler = Handler(manager.inner, postProcessor=manager.post)
        handler(payload, command)

        manager.assert_has_calls([
            call.inner(payload, command),
            call.post(payload, command),
        ])
