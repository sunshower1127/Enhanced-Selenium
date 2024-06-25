import time
import keyboard
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException


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

    def wait(self, secs: float = None, key: str = None):
        secs and time.sleep(secs)
        key and keyboard.wait(key)
        return self.__wait[0]

    def find(self, xpath):
        self.wait().until(EC.presence_of_element_located((By.XPATH, xpath)))
        return Element(self.__wait[0], self.find_element(By.XPATH, xpath))


class Element(WebElement):
    # 지금 이 생성자 수상함. 이렇게 상속받는게 맞나?
    def __init__(self, wait: list[WebDriverWait], element: WebElement):
        self.__wait = wait
        super().__init__(element.parent, element.id)


if __name__ == "__main__":
    driver = ChromeDriver(debug=True)
    driver.get("https://www.google.com")
    a = driver.find_element(By.CLASS_NAME, "a4bIc").find_element(
        By.XPATH, "descendant::textarea"
    )
    print(
        f"{a.accessible_name=}, {a.aria_role=}, {a.rect=}, {a.location_once_scrolled_into_view=}"
    )

# 이제 find_element 여러번 해보는거 ㅇㅇ -> 상대경로로 검색이 되나? 되네요.
