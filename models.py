import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from utils import get_xpath


class ChromeDriver(webdriver.Chrome):
    def __init__(self, debug=False, audio=False, maximize=True):
        self.debug = debug
        options = webdriver.ChromeOptions()
        debug and options.add_experimental_option("detach", True)
        audio or options.add_argument("--mute-audio")

        super().__init__(options=options)
        maximize and self.maximize_window()
        self.__wait: list[WebDriverWait] = [None]
        self.set_internal_wait()

    def set_internal_wait(self, timeout=20, freq=0.5):
        self.__wait[0] = WebDriverWait(self, timeout=timeout, poll_frequency=freq)

    def wait(self, secs=0.0):
        secs and time.sleep(secs)
        return self.__wait[0]

    def find_element(
        self,
        tag="*",
        id: str = None,
        name: str = None,
        css_class: str = None,
        css_class_contains: str = None,
        text: str = None,
        text_contains: str = None,
    ):
        value = get_xpath(
            tag, id, name, css_class, css_class_contains, text, text_contains
        )
        self.wait().until(EC.presence_of_element_located((By.XPATH, value)))
        return Element(self.__wait, super().find_element(By.XPATH, value))

    # def find_elements

    def accept_alert(self):
        self.wait().until(EC.alert_is_present())
        self.switch_to.alert.accept()


class Element(WebElement):
    def __init__(self, wait, element: WebElement):
        self.__wait = wait
        super().__init__(element)

    def __wait(self, secs=0.0):
        secs and time.sleep(secs)
        return self.__wait[0]

    # def find_element

    # def find_elements
