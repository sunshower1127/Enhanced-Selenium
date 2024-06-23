from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


def condition(tag="*", **kwargs):
    """
    [key]

    id, name, css_class, n, text, and other props

    _c -> contains

    _n -> not

    _l -> key < value

    _g -> key > value

    _b -> value1 < key < value2

    [value]

    or -> (value1, value2, ...)

    n하고 _l, _g, _b는 자동으로 int형으로

    나머지는 str형으로 변환됨.
    """

    result = tag

    if not kwargs:
        return result

    result += "["
    for key, value in kwargs.items():
        if result[-1] != "[":
            result += " and "

        """ key 세팅 """
        temp = ""

        if key.startswith("css_class"):
            temp = "@" + key[4:]

        elif key.startswith("text"):
            temp = "text()" + key[4:]

        elif key == "n" or key == "n_l" or key == "n_g" or key == "n_b" or key == "n_n":
            temp = "position()" + key[1:]

        else:
            temp = "@" + key

        if key[-2:] == "_b":
            result += f"({temp[:-2]}>{value[0]} and {temp[:-2]}<{value[1]})"
            continue

        elif key == "n_l":
            temp = f"{temp[:-2]}<" + "{}"

        elif key == "n_g":
            temp = f"{temp[:-2]}>" + "{}"

        elif key[-2:] == "_l":
            temp = f"number({temp[:-2]})<" + "{}"

        elif key[-2:] == "_g":
            temp = f"number({temp[:-2]})>" + "{}"

        elif key[-2:] == "_c":
            temp = f"contains({temp[:-2]}, " + "{})"

        elif key[-2:] == "_n":
            temp = f"{temp[:-2]}!=" + "{}"

        else:
            temp = f"{temp}=" + "{}"
        ########################################

        """ value 세팅 """

        if key[-2:] == "_l" or key[-2:] == "_g":
            result += temp.format(value)
            continue

        value_format = "{}" if key == "n" or key == "n_n" else '"{}"'
        if isinstance(value, (tuple, list)):
            and_or = " and " if key[-2:] == "_n" else " or "
            result += (
                "("
                + and_or.join(temp.format(value_format.format(v)) for v in value)
                + ")"
            )

        else:
            result += temp.format(value_format.format(value))

    result += "]"
    return result


# 추후에 Driver하고 Element를 분리할 예정

chrome_options = webdriver.ChromeOptions()

chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--mute-audio")

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

wait = WebDriverWait(driver, 20)


class Element:
    def __init__(self, element=driver):
        self.current_element = element

    def uncertain(self, func):
        try:
            return func()
        except Exception:
            return

    def set_internal_repeat(self, timeout=20, freq=0.5):
        global wait
        wait = WebDriverWait(driver, timeout=timeout, poll_frequency=freq)

    def wait_secs(self, secs):
        time.sleep(secs)

    def get_url(self, url):
        driver.get(url)

    def switch_iframe(self, *args):
        """
        default -> 가장 바깥 frame

        first -> 안에있는 첫번째 frame

        parent -> 부모 frame
        """
        for id in args:
            if id == "default":
                driver.switch_to.default_content()
                continue

            if id == "parent":
                driver.switch_to.parent_frame()
                continue

            if id == "first":
                path = "//" + condition(tag="iframe")
            else:
                path = "//" + condition(tag="iframe", id=id)

            wait.until(EC.presence_of_element_located((By.XPATH, path)))
            driver.switch_to.frame(driver.find_element(By.XPATH, path))

    def go_back(self):
        driver.back()

    def close_window(self):
        driver.close()

    def close_all_windows(self):
        while driver.window_handles:
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()

    def quit(self):
        driver.quit()

    def switch_window(self, n=1):
        wait.until(EC.number_of_windows_to_be(n))
        driver.switch_to.window(driver.window_handles[n - 1])

    def yes_to_alert(self):
        wait.until(EC.alert_is_present())
        driver.switch_to.alert.accept()

    def execute_js(self, script):
        return driver.execute_script(script)

    def find(self, raw=None, tag="*", **kwargs):
        """
        [key]

        id, name, css_class, n, text, and other props

        _c -> contains

        _n -> not

        _l -> key < value

        _g -> key > value

        _b -> value1 < key < value2

        [value]

        or -> (value1, value2, ...)

        n하고 _l, _g, _b는 자동으로 int형으로

        나머지는 str형으로 변환됨.
        """
        path = raw if raw else "descendant::" + condition(tag, **kwargs)

        wait.until(EC.presence_of_element_located((By.XPATH, path)))

        return Element(self.current_element.find_element(By.XPATH, path))

    def find_all(self, raw=None, tag="*", **kwargs):
        """
        [key]

        id, name, css_class, n, text, and other props

        _c -> contains

        _n -> not

        _l -> key < value

        _g -> key > value

        _b -> value1 < key < value2

        [value]

        or -> (value1, value2, ...)

        n하고 _l, _g, _b는 자동으로 int형으로

        나머지는 str형으로 변환됨.
        """

        path = raw if raw else "descendant::" + condition(tag, **kwargs)

        wait.until(EC.presence_of_all_elements_located((By.XPATH, path)))

        return [
            Element(element)
            for element in self.current_element.find_elements(By.XPATH, path)
        ]

    def parent(self, times=1):
        path = "/".join([".."] * times)
        return Element(self.current_element.find_element(By.XPATH, path))

    def click(self):
        self.current_element.click()

    def send_keys(self, *args):
        self.current_element.send_keys(args)

    def text(self):
        return self.current_element.text

    def screenshot(self, path):
        return self.current_element.screenshot_as_png

    def prop(self, prop):
        return self.current_element.get_attribute(prop)
