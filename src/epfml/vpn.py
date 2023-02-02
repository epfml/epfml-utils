"""
Utilities related to the EPFL network.
"""

import socket


def assert_connected():
    test_url = "s3.epfl.ch"
    if not _url_is_reachable(test_url):
        raise RuntimeError("No VPN connection.")


def _url_is_reachable(url: str, port: int = 80, *, timeout: float = 0.5) -> bool:
    # Based on https://stackoverflow.com/questions/2953462/pinging-servers-in-python.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((url, port))
            s.shutdown(socket.SHUT_RDWR)
            return True
        except socket.gaierror:  # DNS error.
            return False
        except socket.timeout:  # Server did not respond timeout.
            return False
