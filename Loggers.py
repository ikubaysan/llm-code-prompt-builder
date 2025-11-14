import logging
import sys
import io

_MAIN_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

def _make_utf8_stdout():
    """
    Ensure sys.stdout is UTF-8 so logging a.k.a. StreamHandler(sys.stdout) won't choke on Unicode.
    If reconfigure() isn't available (older Python), wrap the buffer.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Py3.7+
        return sys.stdout
    except Exception:
        try:
            return io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        except Exception:
            return sys.stdout

def _add_console_handler(logger, level):
    stream = _make_utf8_stdout()
    console_handler = logging.StreamHandler(stream)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(_MAIN_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)


def configure_console_logger(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    _add_console_handler(logger, level)
