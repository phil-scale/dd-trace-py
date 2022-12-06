from typing import TypeVar
import socket


T = TypeVar("T")


# Returns true if address is an IPv6 address
def is_ipv6_hostname(hostname):
    # type: (str) -> bool
    try:
        socket.inet_pton(socket.AF_INET6, hostname)
        return True
    except socket.error:  # not a valid address
        return False

