from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from utils import get_xpath

if TYPE_CHECKING:
    from models.chrome_driver import ChromeDriver


class Element(WebElement):
    def __init__(self, element: WebElement):
        super().__init__(element.parent, element.id)
        self.driver: ChromeDriver = super().parent

    def parent(self, levels=1):
        xpath = "/".join([".."] * levels)
        self.driver.wait().until(ec.presence_of_element_located((By.XPATH, xpath)))
        return Element(self.find_element(By.XPATH, xpath))

    def find(
        self,
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
            self.driver.wait().until(ec.presence_of_element_located((By.XPATH, xpath)))
        except NoSuchElementException:
            if self.driver.debug:
                self.driver._debug_find(xpath)
            else:
                raise NoSuchElementException(f"Element not found: {xpath}")

        return Element(self.find_element(By.XPATH, xpath))

    def find_all(
        self,
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
                ec.presence_of_all_elements_located((By.XPATH, xpath))
            )
        except NoSuchElementException:
            if self.driver.debug:
                self.driver._debug_find(xpath)
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

    def click(self, by: Literal["default", "enter", "js", "mouse"] = "default"):
        match by:
            case "default":
                super().click()
            case "enter":
                self.send_keys(Keys.ENTER)
            case "js":
                self.driver.execute_script("arguments[0].click();", self)
            case "mouse":
                ActionChains(self._parent).click(self).perform()

    def select(
        self, by: Literal["index", "value", "text"] = "index", value: str | int = 0
    ):
        select = Select(self)
        match by:
            case "index":
                select.select_by_index(int(value))
            case "value":
                select.select_by_value(str(value))
            case "text":
                select.select_by_visible_text(str(value))


class Elements:
    def __init__(self, elements: list[Element]):
        self.__elements = elements
        self.__index = 0
        self.texts = [element.text for element in self.__elements]

    def __getitem__(self, index: int):
        return self.__elements[index]

    def __iter__(self):
        self.__index = 0
        return self

    def __next__(self):
        if self.__index < len(self.__elements):
            result = self.__elements[self.__index]
            self.__index += 1
            return result

        raise StopIteration

    def parents(self, levels=1, *, partial=False):
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

    def click(self, by: Literal["default", "enter", "js", "mouse"] = "default"):
        match by:
            case "default":
                for element in self.__elements:
                    element.click()

            case "enter":
                for element in self.__elements:
                    element.send_keys(Keys.ENTER)

            case "js":
                self.__elements[0].driver.execute_script(
                    "arguments.forEach(e => e.click());", *self.__elements
                )

            case "mouse":
                actions = ActionChains(self.__elements[0].driver)
                for element in self.__elements:
                    actions.click(element)
                actions.perform()

    def send_keys(self, keys: str | list[str]):
        if isinstance(keys, str):
            for element in self.__elements:
                element.send_keys(keys)

        else:
            for element, key in zip(self.__elements, keys):
                element.send_keys(key)

    def attributes(
        self,
        name: str,
    ):
        return [element.get_attribute(name) for element in self.__elements]
