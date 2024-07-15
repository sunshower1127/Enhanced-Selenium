from __future__ import annotations

import os
import time
from typing import Literal

import keyboard
from models.element import Element, Elements
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from utils import get_xpath


class ChromeDriver(webdriver.Chrome):
    def __init__(
        self,
        *,
        keep_alive=False,
        audio=False,
        maximize=True,
        headless=False,
        popup=True,
        info_bar=True,
    ):
        self.debug = os.environ.get("ES_DEBUG") == "1"
        options = webdriver.ChromeOptions()
        if keep_alive:
            options.add_experimental_option("detach", value=True)
        if not audio:
            options.add_argument("--mute-audio")
        if maximize:
            options.add_argument("--start-maximized")
        if headless:
            options.add_argument("--headless")
        if not popup:
            options.add_argument("--disable-popup-blocking")
        if not info_bar:
            options.add_argument("--disable-infobars")

        super().__init__(options=options)
        self.implicitly_wait()

    def __del__(self):
        self.quit()

    def implicitly_wait(self, timeout=20.0, freq=0.5):
        self.__wait = WebDriverWait(self, timeout=timeout, poll_frequency=freq)

    def wait(self, secs: float = 0.0, key: str = ""):
        if secs:
            time.sleep(secs)
        if key:
            keyboard.wait(key)
        return self.__wait

    def find(
        self,
        xpath="",
        *,
        axis: Literal[
            "ancestor",
            "ancestor-or-self",
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
    ):
        if not xpath:
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
                self._debug_find(xpath)
            else:
                # raise NoSuchElementException(f"Element not found: {xpath}") from e
                pass

        return Element(self.find_element(By.XPATH, xpath))

    def find_all(
        self,
        xpath="",
        *,
        axis: Literal[
            "ancestor",
            "ancestor-or-self",
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
                self._debug_find(xpath)
            else:
                raise NoSuchElementException(f"Element not found: {xpath}")

        return Elements(
            [Element(element) for element in self.find_elements(By.XPATH, xpath)],
        )

    def close_all(self):
        # quit이랑 비교해봐야함.
        for window_handle in self.window_handles:
            self.switch_to.window(window_handle)
            self.close()

    def goto_frame(self, name: str | list[str] = "default"):
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
        if i >= len(self.window_handles):
            self.wait().until(EC.number_of_windows_to_be(i + 1))
        self.switch_to.window(self.window_handles[i])

    def goto_alert(self):
        self.wait().until(EC.alert_is_present())
        return self.switch_to.alert

    def goto_focused_element(self):
        return Element(self.switch_to.active_element)

    def _debug_find(self, xpath: str):
        """
        모든 window와 frame을 탐색하면서 element를 찾는다.
        찾으면 window와 frame을 이동해줌.
        """
        N = 10
        answers: list[tuple[int, list[str]]] = []
        _timeout = self.wait()._timeout
        _poll = self.wait()._poll
        self.implicitly_wait(1, 0.1)

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
                self.implicitly_wait(_timeout, _poll)
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

            outputs = cur_window_outputs + other_window_outputs
            print(f"ES Debugger: Element found in the following context\n{xpath=}")
            for i, output in enumerate(outputs):
                print(f"#{i + 1}")
                print(output)

            self.implicitly_wait(_timeout, _poll)
            user_input = input(
                "ES Debugger: Select the context you want to use [1, 2, ...] / [N]o "
            )
            while user_input.lower() not in [
                str(i) for i in range(1, len(outputs) + 1)
            ] + ["n"]:
                user_input = input()
            if user_input.lower() == "n":
                self.implicitly_wait(_timeout, _poll)
                raise NoSuchElementException

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
            self.implicitly_wait(_timeout, _poll)
            return

        self.implicitly_wait(_timeout, _poll)
        # 디버거 에러처리 -> 다시 시작? 물어보고, 물어봤으면 quit해주고 exit.
        # raise NoSuchElementException(f"ES Debugger: Element not found\n{xpath=}")