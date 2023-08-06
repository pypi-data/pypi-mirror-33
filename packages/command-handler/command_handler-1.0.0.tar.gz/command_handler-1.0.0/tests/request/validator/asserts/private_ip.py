from unittest import TestCase
from unittest.mock import MagicMock

from command_handler.request.validator.asserts import privateIp
from command_handler.request.validator.exceptions import AssertionFailedException


class PrivateIpRequestValidatorTest(TestCase):
    def testRaisesExceptionWhenRequestRemoteAddrIsNotPrivate(self):
        request = MagicMock()
        request.remote_addr = "11.12.13.14"

        with self.assertRaises(AssertionFailedException) as cm:
            privateIp(request)

        self.assertEqual(cm.exception.code, 403)
        self.assertEqual(str(cm.exception), "Remote address is not private")

    def testReturnsNoneWhenRequestRemoteAddrIsPrivate(self):
        request = MagicMock()
        request.remote_addr = "127.0.123.45"

        self.assertIsNone(privateIp(request))
