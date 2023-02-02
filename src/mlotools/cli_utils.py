import contextlib
import sys

@contextlib.contextmanager
def nicely_print_runtime_errors():
    try:
        yield
    except RuntimeError as e:
        print(_red_background(" Error "), e)
        sys.exit(1)

def _red_background(text: str) -> str:
    return "\033[41m" + text + "\033[0m"
