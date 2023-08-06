from ipaddress import ip_address

from command_handler.request.validator.exceptions import AssertionFailedException


def privateIp(request):
    try:
        assert ip_address(request.remote_addr).is_private, "Remote address is not private"
    except AssertionError as e:
        raise AssertionFailedException(str(e), 403) from e
