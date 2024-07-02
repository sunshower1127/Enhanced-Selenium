import time
from typing import Literal
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

from utils import get_xpath


class ChromeDriver(webdriver.Chrome):
    def __init__(self, debug=False, audio=False, maximize=True):
        self.debug = debug
        options = webdriver.ChromeOptions()
        if debug:
            options.add_experimental_option("detach", True)
        if not audio:
            options.add_argument("--mute-audio")

        super().__init__(options=options)
        if maximize:
            self.maximize_window()
        self.set_internal_wait()

    def set_internal_wait(self, timeout=20.0, freq=0.5):
        self.__wait = WebDriverWait(self, timeout=timeout, poll_frequency=freq)

    def wait(self, secs: float = 0.0, key: str = ""):
        if secs:
            time.sleep(secs)
        if key:
            keyboard.wait(key)
        return self.__wait

    def find(
        self,
        axis: Literal[
            "ancestor",
            "ansestor-or-self",
            "child",
            "descendant",
            "descendant-or-self",
            "following",
            "following-sibling",
            "parent",
            "preceding",
            "preceding-sibling",
        ] = "descendant",
        tag="*",
        id: str | list[str] | None = None,
        name: str | list[str] | None = None,
        css_class: str | list[str] | None = None,
        css_class_contains: str | list[str] | None = None,
        text: str | list[str] | None = None,
        text_contains: str | list[str] | None = None,
        text_not: str | list[str] | None = None,
        text_not_contains: str | list[str] | None = None,
        xpath: str | None = None,
    ):
        if xpath is None:
            xpath = get_xpath(
                axis=axis,
                tag=tag,
                id=id,
                name=name,
                css_class=css_class,
                css_class_contains=css_class_contains,
                text=text,
                text_contains=text_contains,
                text_not=text_not,
                text_not_contains=text_not_contains,
            )

        try:
            self.wait().until(EC.presence_of_element_located((By.XPATH, xpath)))
        except NoSuchElementException:
            if self.debug:
                self.__debug_find(xpath)
            else:
                raise NoSuchElementException(f"Element not found: {xpath}")

        return Element(self.find_element(By.XPATH, xpath))

    def find_all(
        self,
        axis: Literal[
            "ancestor",
            "ansestor-or-self",
            "child",
            "descendant",
            "descendant-or-self",
            "following",
            "following-sibling",
            "parent",
            "preceding",
            "preceding-sibling",
        ] = "descendant",
        tag="*",
        id: str | list[str] | None = None,
        name: str | list[str] | None = None,
        css_class: str | list[str] | None = None,
        css_class_contains: str | list[str] | None = None,
        text: str | list[str] | None = None,
        text_contains: str | list[str] | None = None,
        text_not: str | list[str] | None = None,
        text_not_contains: str | list[str] | None = None,
        xpath: str | None = None,
    ):
        if xpath is None:
            xpath = get_xpath(
                axis=axis,
                tag=tag,
                id=id,
                name=name,
                css_class=css_class,
                css_class_contains=css_class_contains,
                text=text,
                text_contains=text_contains,
                text_not=text_not,
                text_not_contains=text_not_contains,
            )

        try:
            self.wait().until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        except NoSuchElementException:
            if self.debug:
                self.__debug_find(xpath)
            else:
                raise NoSuchElementException(f"Element not found: {xpath}")

        return Elements(
            [Element(element) for element in self.find_elements(By.XPATH, xpath)],
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
        if isinstance(name, str):
            name = [name]

        if name[0] == "default":
            self.switch_to.default_content()
        elif name[0] == "parent":
            self.switch_to.parent_frame()
        else:
            self.wait().until(EC.frame_to_be_available_and_switch_to_it(name[0]))

        if len(name) > 1:
            self.goto_frame(name[1:])

    def goto_window(self, i=0):
        # 이건 근데 좀 고쳐보고 싶음
        if len(self.window_handles) <= i + 1:
            self.wait().until(EC.number_of_windows_to_be(i + 1))
        self.switch_to.window(self.window_handles[i])

    def goto_alert(self):
        self.wait().until(EC.alert_is_present())
        return self.switch_to.alert

    def goto_focused_element(self):
        return Element(self.switch_to.active_element)

    def __debug_find(self, xpath: str):
        """
        모든 window와 frame을 탐색하면서 element를 찾는다.
        찾으면 window와 frame을 이동해줌.
        """
        N = 10
        answers: list[tuple[int, list[str]]] = []

        _timeout = self.wait()._timeout
        _poll = self.wait()._poll
        self.set_internal_wait(1, 0.1)

        def dfs():
            try:
                self.find(xpath=xpath)
                answers.append((window_i, [*frame_path]))
            except NoSuchElementException:
                pass

            try:
                iframe_names = self.find_all(tag="iframe").attributes("name")
                for iframe_name in iframe_names:
                    if iframe_name is None:
                        continue
                    self.goto_frame(iframe_name)
                    frame_path.append(iframe_name)
                    dfs()
                    self.goto_frame("parent")
                    frame_path.pop()
            except NoSuchElementException:
                return

        for _ in range(N):
            for window_i, window_handle in enumerate(self.window_handles):
                frame_path: list[str] = ["default"]
                self.switch_to.window(window_handle)
                dfs()

            if not answers:
                continue

            cur_window_outputs: list[str] = []
            other_window_outputs: list[str] = []
            for window, frame in answers:
                output = ""
                if window != self.window_handles.count(self.current_window_handle):
                    output += f"driver.goto_window({window})\n"
                output += f'driver.goto_frame("{'", "'.join(frame)}")\n'
                if window == self.window_handles.count(self.current_window_handle):
                    cur_window_outputs.append(output)
                else:
                    other_window_outputs.append(output)

            # 여기서 부터 코딩하면 됨.
            outputs = cur_window_outputs + other_window_outputs
            print(f"ES Debugger: Element found in the following context\n{xpath=}")
            for i, output in enumerate(outputs):
                print(f"#{i + 1}")
                print(output)

            self.set_internal_wait(_timeout, _poll)
            user_input = input(
                "ES Debugger: Select the context you want to use [1, 2, ...] / [N]o"
            )
            while user_input.lower() not in [
                str(i) for i in range(1, len(outputs) + 1)
            ] + ["n"]:
                user_input = input()
            if user_input.lower() == "n":
                raise NoSuchElementException()

            user_input = int(user_input)
            user_output = outputs[user_input - 1]

            def extract_between(text, start, end):
                start_index = text.find(start)
                if start_index == -1:
                    return ""  # 시작 문자열이 없으면 빈 문자열 반환
                start_index += len(start)  # 시작 문자열의 끝으로 인덱스 이동

                end_index = text.find(end, start_index)
                if end_index == -1:
                    return ""  # 종료 문자열이 없으면 빈 문자열 반환

                return text[start_index:end_index]

            if (window_str := extract_between(user_output, "window(", ")")) != "":
                self.goto_window(int(window_str))

            if (frame_str := extract_between(user_output, 'frame("', '")')) != "":
                self.goto_frame(frame_str.split('", "'))

            return

        self.set_internal_wait(_timeout, _poll)
        raise NoSuchElementException(f"ES Debugger: Element not found\n{xpath=}")

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
    def __init__(self, element: WebElement):
        super().__init__(element.parent, element.id)
        self.driver: ChromeDriver = super().parent

    def parent(self, levels=1):
        xpath = "/".join([".."] * levels)
        self.driver.wait().until(EC.presence_of_element_located((By.XPATH, xpath)))
        return Element(self.find_element(By.XPATH, xpath))

    def find(
        self,
        axis: Literal[
            "ancestor",
            "ansestor-or-self",
            "child",
            "descendant",
            "descendant-or-self",
            "following",
            "following-sibling",
            "parent",
            "preceding",
            "preceding-sibling",
        ] = "descendant",
        tag="*",
        id: str | list[str] | None = None,
        name: str | list[str] | None = None,
        css_class: str | list[str] | None = None,
        css_class_contains: str | list[str] | None = None,
        text: str | list[str] | None = None,
        text_contains: str | list[str] | None = None,
        text_not: str | list[str] | None = None,
        text_not_contains: str | list[str] | None = None,
        xpath: str | None = None,
    ):
        if xpath is None:
            xpath = get_xpath(
                axis=axis,
                tag=tag,
                id=id,
                name=name,
                css_class=css_class,
                css_class_contains=css_class_contains,
                text=text,
                text_contains=text_contains,
                text_not=text_not,
                text_not_contains=text_not_contains,
            )

        try:
            self.driver.wait().until(EC.presence_of_element_located((By.XPATH, xpath)))
        except NoSuchElementException:
            if self.driver.debug:
                self.driver.__debug_find(xpath)
            else:
                raise NoSuchElementException(f"Element not found: {xpath}")

        return Element(self.find_element(By.XPATH, xpath))

    def find_all(
        self,
        axis: Literal[
            "ancestor",
            "ansestor-or-self",
            "child",
            "descendant",
            "descendant-or-self",
            "following",
            "following-sibling",
            "parent",
            "preceding",
            "preceding-sibling",
        ] = "descendant",
        tag="*",
        id: str | list[str] | None = None,
        name: str | list[str] | None = None,
        css_class: str | list[str] | None = None,
        css_class_contains: str | list[str] | None = None,
        text: str | list[str] | None = None,
        text_contains: str | list[str] | None = None,
        text_not: str | list[str] | None = None,
        text_not_contains: str | list[str] | None = None,
        xpath: str | None = None,
    ):
        if xpath is None:
            xpath = get_xpath(
                axis=axis,
                tag=tag,
                id=id,
                name=name,
                css_class=css_class,
                css_class_contains=css_class_contains,
                text=text,
                text_contains=text_contains,
                text_not=text_not,
                text_not_contains=text_not_contains,
            )

        try:
            self.driver.wait().until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
        except NoSuchElementException:
            if self.driver.debug:
                self.driver.__debug_find(xpath)
            else:
                raise NoSuchElementException(f"Element not found: {xpath}")

        return Elements(
            [Element(element) for element in self.find_elements(By.XPATH, xpath)],
        )

    def move_mouse(self, offset_x=0, offset_y=0):
        ActionChains(self._parent).move_to_element_with_offset(
            self, offset_x, offset_y
        ).perform()
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
        self.__index = 0
        self.texts = [element.text for element in self.__elements]

    def __getitem__(self, index):
        return self.__elements[index]

    def __iter__(self):
        self.__index = 0
        return self

    def __next__(self):
        if self.__index < len(self.__elements):
            result = self.__elements[self.__index]
            self.__index += 1
            return result
        else:
            raise StopIteration

    def parents(self, levels=1, partial=False):
        if not partial:
            return Elements([element.parent(levels) for element in self.__elements])

        result: list[Element] = []
        for element in self.__elements:
            try:
                result.append(element.parent(levels))
            except NoSuchElementException:
                pass
        return Elements(result)

    def find(
        self,
        axis: Literal[
            "ancestor",
            "ansestor-or-self",
            "child",
            "descendant",
            "descendant-or-self",
            "following",
            "following-sibling",
            "parent",
            "preceding",
            "preceding-sibling",
        ] = "descendant",
        tag="*",
        id: str | list[str] | None = None,
        name: str | list[str] | None = None,
        css_class: str | list[str] | None = None,
        css_class_contains: str | list[str] | None = None,
        text: str | list[str] | None = None,
        text_contains: str | list[str] | None = None,
        text_not: str | list[str] | None = None,
        text_not_contains: str | list[str] | None = None,
        xpath: str | None = None,
        partial=False,
    ):
        if xpath is None:
            xpath = get_xpath(
                axis=axis,
                tag=tag,
                id=id,
                name=name,
                css_class=css_class,
                css_class_contains=css_class_contains,
                text=text,
                text_contains=text_contains,
                text_not=text_not,
                text_not_contains=text_not_contains,
            )

        if not partial:
            return Elements([element.find(xpath=xpath) for element in self.__elements])

        result: list[Element] = []
        try:
            result.append(self.__elements[0].find(xpath=xpath))
        except NoSuchElementException:
            pass

        for element in self.__elements[1:]:
            try:
                result.append(Element(element.find_element(By.XPATH, xpath)))
            except NoSuchElementException:
                pass
        return Elements(result)

    def click(self):
        return [element.click() for element in self.__elements]

    def send_keys(self, keys: str | list[str]):
        if isinstance(keys, str):
            return [element.send_keys(keys) for element in self.__elements]
        else:
            return [
                element.send_keys(key) for element, key in zip(self.__elements, keys)
            ]

    def attributes(
        self,
        name: str,
    ):
        return [element.get_attribute(name) for element in self.__elements]


class SeleniumDebugger:
    def run(self, path):
        while True:
            result = subprocess.run(
                "python " + path, shell=True, text=True, capture_output=True
            )
            if result.returncode == 0:
                print("ES Debugger: Program executed successfully")
            else:
                print("ES Debugger: Program failed to execute")
                print(result.stderr)

            user_input = input("ES Debugger: Do you want to retry? [R]etry / [Q]uit")
            while user_input.lower() not in ["r", "q"]:
                user_input = input()
            if user_input.lower() != "r":
                break


class SeleniumBuilder:
    # 1. tkinter를 활용해서 GUI 구축
    # 2. 빌드 기능
    ...
