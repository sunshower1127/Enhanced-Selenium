import time

from selenium.common.exceptions import TimeoutException


def retry_on_timeout(timeout, freq):
    def decorator(func):
        def wrapper(*args, **kwargs):
            end_time = time.time() + timeout
            while time.time() < end_time:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    pass
                time.sleep(freq)
            raise TimeoutException(
                f"Function {func.__name__} timed out after {timeout} seconds"
            )

        return wrapper

    return decorator
