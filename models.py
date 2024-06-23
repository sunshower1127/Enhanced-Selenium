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

    def wait(self, secs: float = None, key: str = None):
        secs and time.sleep(secs)
        key and keyboard.wait(key)
        return self.__wait[0]

    def find(
        self,
        tag="*",
        id: str | list[str] = None,
        name: str | list[str] = None,
        css_class: str | list[str] = None,
        css_class_contains: str | list[str] = None,
        text: str | list[str] = None,
        text_contains: str | list[str] = None,
        text_not: str | list[str] = None,
        text_not_contains: str | list[str] = None,
    ):
        value = get_xpath(
            tag,
            id,
            name,
            css_class,
            css_class_contains,
            text,
            text_contains,
            text_not,
            text_not_contains,
        )
        self.wait().until(EC.presence_of_element_located((By.XPATH, value)))
        return Element(self.__wait, self.find_element(By.XPATH, value))

    def find_all(
        self,
        tag="*",
        id: str | list[str] = None,
        name: str | list[str] = None,
        css_class: str | list[str] = None,
        css_class_contains: str | list[str] = None,
        text: str | list[str] = None,
        text_contains: str | list[str] = None,
        text_not: str | list[str] = None,
        text_not_contains: str | list[str] = None,
    ):
        value = get_xpath(
            tag,
            id,
            name,
            css_class,
            css_class_contains,
            text,
            text_contains,
            text_not,
            text_not_contains,
        )
        self.wait().until(EC.presence_of_all_elements_located((By.XPATH, value)))
        return Elements(
            [
                Element(self.__wait, element)
                for element in self.find_elements(By.XPATH, value)
            ],
        )

    def close_all(self):
        # quit이랑 비교해봐야함.
        while self.window_handles:
            # current_window_handle이랑 뭐가다름
            self.switch_to.window(self.window_handles[-1])
            # self.switch_to.new_window() 이걸로 대체 가능?
            self.close()

    def goto_frame(self, name: str | list[str] = "default"):
        # 얘도 고쳐보고 싶음.
        isinstance(name, str) and (name := [name])

        if name[0] == "default":
            self.switch_to.default_content()
        elif name[0] == "parent":
            self.switch_to.parent_frame()
        else:
            self.wait().until(EC.presence_of_element_located((By.NAME, name)))
            self.switch_to.frame(name)

        len(name) == 1 or self.goto_frame(name[1:])

    def goto_window(self, n=1):
        # 이건 근데 좀 고쳐보고 싶음
        self.wait().until(EC.number_of_windows_to_be(n))
        self.switch_to.window(self.window_handles[n - 1])

    def goto_alert(self):
        self.wait().until(EC.alert_is_present())
        return self.switch_to.alert

    def goto_focused(self):
        return Element(self.__wait, self.switch_to.active_element)

    # 1. switch_to -> alert, frame, window, active_element, default_content, parent_frame
    # 얘네들을 어떻게 해야할지. -> 후처리 같은거 -> 일단 세세한 기능들 한 번 알아봐야할듯.
    # 윈도우 tab하고 window 다른점하고 new_window는 뭔지. current_window_handle이랑 window_handles 차이점.
    # frame에 int 인자 넣는건 뭔지. 꼭 default_frame 거쳐야하는지 등등...
    # 2. 디버깅 모드는 어떻게 만들건지.
    # 3. get_xpath 자주 사용하는 것 위주로? 아니면 xpath에서 지원하는 것들 전부 지원?
    # 4. 에러처리는 어떻게 할것인지.
    # 5. 키보드, 마우스 이벤트는 어떻게 할것인지. v


class Element(WebElement):
    # 지금 이 생성자 수상함. 이렇게 상속받는게 맞나?
    def __init__(self, wait: list[WebDriverWait], element: WebElement):
        self.__wait = wait
        super().__init__(element.parent, element.id)

    def __wait(self, secs=0.0):
        secs and time.sleep(secs)
        return self.__wait[0]

    def find(
        self,
        tag="*",
        id: str | list[str] = None,
        name: str | list[str] = None,
        css_class: str | list[str] = None,
        css_class_contains: str | list[str] = None,
        text: str | list[str] = None,
        text_contains: str | list[str] = None,
        text_not: str | list[str] = None,
        text_not_contains: str | list[str] = None,
    ):
        value = get_xpath(
            tag,
            id,
            name,
            css_class,
            css_class_contains,
            text,
            text_contains,
            text_not,
            text_not_contains,
        )
        self.wait().until(EC.presence_of_element_located((By.XPATH, value)))
        return Element(self.__wait, self.find_element(By.XPATH, value))

    def find_all(
        self,
        tag="*",
        id: str | list[str] = None,
        name: str | list[str] = None,
        css_class: str | list[str] = None,
        css_class_contains: str | list[str] = None,
        text: str | list[str] = None,
        text_contains: str | list[str] = None,
        text_not: str | list[str] = None,
        text_not_contains: str | list[str] = None,
    ):
        value = get_xpath(
            tag,
            id,
            name,
            css_class,
            css_class_contains,
            text,
            text_contains,
            text_not,
            text_not_contains,
        )
        self.wait().until(EC.presence_of_all_elements_located((By.XPATH, value)))
        return Elements(
            [
                Element(self.__wait, element)
                for element in self.find_elements(By.XPATH, value)
            ],
        )

    def move_mouse(self):
        ActionChains(self._parent).move_to_element(self).perform()
        return self

    def click_by_mouse(self):
        ActionChains(self._parent).click(self).perform()
        return self

    def select_by_index(self, index: int):
        Select(self).select_by_index(index)
        return self


class Elements:
    def __init__(self, elements: list[Element]):
        self.__elements = elements
        self.texts = [element.text for element in self.__elements]
        self.parents = [element.parent for element in self.__elements]

    def get(self, index=0):
        return self.__elements[index]

    def get_all(self):
        return self.__elements

    def __wait(self, secs=0.0):
        secs and time.sleep(secs)
        return self.__wait[0]

    def find(self):
        return [element.find() for element in self.__elements]

    def click(self):
        return [element.click() for element in self.__elements]

    def send_keys(self, keys: str | list[str]):
        if isinstance(keys, str):
            return [element.send_keys(keys) for element in self.__elements]
        else:
            return [
                element.send_keys(key) for element, key in zip(self.__elements, keys)
            ]


class SeleniumDebugger:
    def run(path):
        while True:
            result = subprocess.run(
                "python " + path, shell=True, text=True, capture_output=True
            )
            if result.returncode == 0:
                print("Selenium Debugger: Program executed successfully")
                break
            else:
                print("Selenium Debugger: Program failed to execute")
                print(result.stderr)
                user_input = input(
                    "Selenium Debugger: Do you want to retry? [R]etry / [Q]uit"
                )
                while user_input.lower() not in ["r", "q"]:
                    user_input = input()
                if user_input.lower() != "r":
                    break
