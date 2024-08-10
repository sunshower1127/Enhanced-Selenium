from models.core.driver import ChromeDriver
from selenium.common.exceptions import TimeoutException


class NoError:
    def __init__(self, driver: ChromeDriver):
        self.driver = driver

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return exc_type == TimeoutException


class RepeatSettings:
    def __init__(self, driver: ChromeDriver, timeout=None, freq=None):
        self.driver = driver
        self.orig_timeout = self.driver.wait()._timeout
        self.orig_freq = self.driver.wait()._poll

        self.timeout = timeout or self.orig_timeout
        self.freq = freq or self.orig_freq

    def __enter__(self):
        self.driver.implicitly_wait(timeout=self.timeout, freq=self.freq)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.implicitly_wait(timeout=self.orig_timeout, freq=self.orig_freq)
        return False  # 예외를 억제하지 않음
