from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from utils import get_xpath

if TYPE_CHECKING:
    from driver import ChromeDriver


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
