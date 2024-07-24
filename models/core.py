from __future__ import annotations

import os
import time
from collections import namedtuple
from typing import Callable, Literal

import keyboard
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from utils import get_xpath

# --------------------------------------------------------------------------------------


# Interface for find, find_all
class Findable:
    # From other classes
    _driver: ChromeDriver
    find_element: Callable[[str, str], WebElement]
    find_elements: Callable[[str, str], list[WebElement]]

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
        **kwargs: str | list[str],
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
                **kwargs,
            )

        try:
            self._driver.wait().until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException as e:
            if self._driver.debug:
                self._driver._debugfinder.find(xpath)
            else:
                msg = f"Element not found: {xpath}"
                raise NoSuchElementException(msg) from e

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
        **kwargs: str | list[str],
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
                **kwargs,
            )

        try:
            self._driver.wait().until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
        except TimeoutException as e:
            if self._driver.debug:
                self._driver._debugfinder.find(xpath)
            else:
                msg = f"Element not found: {xpath}"
                raise NoSuchElementException(msg) from e

        return Elements(
            [Element(element) for element in self.find_elements(By.XPATH, xpath)],
        )


# --------------------------------------------------------------------------------------


# for debug_find
class DebugFinder:
    def __init__(self, driver: ChromeDriver):
        self.driver = driver
        self.answers = []
        self.Env = namedtuple("Env", ["timeout", "poll", "win_h"])

    def setup_env(self):
        timeout = self.driver.wait()._timeout
        poll = self.driver.wait()._poll
        self.driver.implicitly_wait(1, 0.1)
        self.driver.debug = False
        win_h = self.driver.current_window_handle
        self.env = self.Env(timeout, poll, win_h)

    def restore_env(self):
        timeout, poll, win_h = self.env
        self.driver.implicitly_wait(timeout, poll)
        self.driver.debug = True
        self.driver.switch_to.window(win_h)
        self.driver.switch_to.default_content()

    def find(self, xpath: str, N=10):
        self.setup_env()
        answers = []

        for _ in range(N):
            for win_i, win_h in enumerate(self.driver.window_handles):
                frame_path: list[str] = ["default"]
                self.driver.switch_to.window(win_h)
                self._dfs(answers, xpath, win_i, frame_path)

            if answers:
                break

        if not answers:
            raise NoSuchElementException
        print(f"ES Debugger: Element found in the following context\n{xpath=}")
        print(self._get_message(answers))

        if (
            user_input := self._get_user_input(
                "ES Debugger: Select the context you want to use [1, 2, ...] / [N]o :",
                len(answers),
            )
        ) == "n":
            raise NoSuchElementException

        user_input = int(user_input)
        win_i, frame = answers[user_input - 1]
        self.driver.goto_window(win_i)
        self.driver.goto_frame(frame)

        self.restore_env()

    def _dfs(self, answers, xpath, win_i, frame_path):
        # find element
        try:
            self.driver.find(xpath)
            answers.append((win_i, [*frame_path]))
        except:
            print("element 못찾음")

        # find iframe
        try:
            iframe_names = self.driver.find_all(tag="iframe").attributes("name")
            for iframe_name in iframe_names:
                if iframe_name is None:
                    continue
                self.driver.goto_frame(iframe_name)
                frame_path.append(iframe_name)
                self._dfs(answers, xpath, win_i, frame_path)
                self.driver.goto_frame("parent")
                frame_path.pop()
        except:
            print("iframe 못찾음")

    def _get_message(self, answers):
        cur_window_outputs: list[str] = []
        other_window_outputs: list[str] = []
        for window, frame in answers:
            output = ""
            if window != self.driver.window_handles.index(self.env.win_h):
                output += f"driver.goto_window({window})\n"
            output += f'driver.goto_frame("{'", "'.join(frame)}")\n'
            if window == self.driver.window_handles.index(self.env.win_h):
                cur_window_outputs.append(output)
            else:
                other_window_outputs.append(output)

        outputs = cur_window_outputs + other_window_outputs
        return "\n".join(f"#{i + 1}\n{output}" for i, output in enumerate(outputs))

    def _get_user_input(self, message, n):
        user_input = input(message)
        while user_input.lower() not in [str(i) for i in range(1, n + 1)] + ["n"]:
            user_input = input()
        return user_input.lower()


# --------------------------------------------------------------------------------------


class ChromeDriver(webdriver.Chrome, Findable):
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
        self._driver = self
        self._debugfinder = DebugFinder(self)

    def __del__(self):
        self.quit()

    def implicitly_wait(self, timeout=20.0, freq=0.5):
        self._wait = WebDriverWait(self, timeout=timeout, poll_frequency=freq)

    def wait(self, secs: float = 0.0, key: str = ""):
        if secs:
            time.sleep(secs)
        if key:
            keyboard.wait(key)
        return self._wait

    def add_key_listener(self, key: str, callback: Callable):
        keyboard.add_hotkey(key, callback)

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
        """
        i가 실제 window의 순서와 다를 수 있음.
        """
        if i >= len(self.window_handles):
            self.wait().until(EC.number_of_windows_to_be(i + 1))
        self.switch_to.window(self.window_handles[i])

    def goto_alert(self):
        self.wait().until(EC.alert_is_present())
        return self.switch_to.alert

    def goto_focused_element(self):
        return Element(self.switch_to.active_element)


# --------------------------------------------------------------------------------------


class Element(WebElement, Findable):
    def __init__(self, element: WebElement):
        super().__init__(element.parent, element.id)
        self._driver: ChromeDriver = super().parent

    def up(self, levels=1):
        xpath = "/".join([".."] * levels)
        self._driver.wait().until(EC.presence_of_element_located((By.XPATH, xpath)))
        return Element(self.find_element(By.XPATH, xpath))

    def move_mouse(self, offset_x=0, offset_y=0):
        ActionChains(self._parent).move_to_element_with_offset(
            self, offset_x, offset_y
        ).perform()
        return self

    def click(self, by: Literal["default", "enter", "js", "mouse"] = "default"):
        match by:
            case "default":
                super().click()
            case "enter":
                self.send_keys(Keys.ENTER)
            case "js":
                self._driver.execute_script("arguments[0].click();", self)
            case "mouse":
                ActionChains(self._parent).click(self).perform()

    def select(
        self,
        by: Literal["index", "value", "text"] = "index",
        value: str | int = 0,
    ):
        select = Select(self)
        match by:
            case "index":
                select.select_by_index(int(value))
            case "value":
                select.select_by_value(str(value))
            case "text":
                select.select_by_visible_text(str(value))


# --------------------------------------------------------------------------------------


class Elements:
    def __init__(self, elements: list[Element]):
        self._elements = elements
        self._index = 0
        self.texts = [element.text for element in self._elements]

    def __getitem__(self, index: int):
        return self._elements[index]

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._elements):
            result = self._elements[self._index]
            self._index += 1
            return result

        raise StopIteration

    def up(self, levels=1, *, partial=False):
        if not partial:
            return Elements([element.parent(levels) for element in self._elements])

        result: list[Element] = []
        for element in self._elements:
            try:
                result.append(element.parent(levels))
            except NoSuchElementException:
                pass

        return Elements(result)

    def find(
        self,
        tag="*",
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
            return Elements([element.find(xpath=xpath) for element in self._elements])

        result: list[Element] = []
        try:
            result.append(self._elements[0].find(xpath=xpath))
        except NoSuchElementException:
            pass

        for element in self._elements[1:]:
            try:
                result.append(Element(element.find_element(By.XPATH, xpath)))
            except NoSuchElementException:
                pass

        return Elements(result)

    def click(self, by: Literal["default", "enter", "js", "mouse"] = "default"):
        match by:
            case "default":
                for element in self._elements:
                    element.click()

            case "enter":
                for element in self._elements:
                    element.send_keys(Keys.ENTER)

            case "js":
                self._elements[0]._driver.execute_script(
                    "arguments.forEach(e => e.click());", *self._elements
                )

            case "mouse":
                actions = ActionChains(self._elements[0]._driver)
                for element in self._elements:
                    actions.click(element)
                actions.perform()

    def send_keys(self, keys: str | list[str]):
        if isinstance(keys, str):
            for element in self._elements:
                element.send_keys(keys)

        else:
            for element, key in zip(self._elements, keys):
                element.send_keys(key)

    def attributes(
        self,
        name: str,
    ):
        return [element.get_attribute(name) for element in self._elements]
