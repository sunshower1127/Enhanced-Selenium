from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from typing import Callable, Tuple

import keyboard
from models.core.debug_finder import DebugFinder
from models.core.findable_element import Element, Findable
from models.withs import ImplicitWaitSettings, NoError
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


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
        super().implicitly_wait(0)
        self.implicitly_wait()
        self._driver = self
        self._debugfinder = DebugFinder(self)
        self.no_error = NoError(self)

    def __del__(self):
        if self.debug:
            self.quit()

    def set_wait(self, timeout: float | None = None, freq: float | None = None):
        return ImplicitWaitSettings(self, timeout, freq)

    def uncertain(
        self,
        func,
        *,
        timeout=5.0,
        freq=0.5,
    ):
        try:
            orig_timeout = self._wait._timeout
            orig_freq = self._wait._poll
            orig_debug = self.debug
            self.implicitly_wait(timeout=timeout, freq=freq)
            self.debug = False
            return func()
        except Exception:
            return None
        finally:
            self.implicitly_wait(timeout=orig_timeout, freq=orig_freq)
            self.debug = orig_debug

    def uncertain_find_and_click(
        self,
        xpath,
        *,
        timeout=5.0,
        freq=0.5,
    ):
        for _ in range(int(timeout / freq)):
            try:
                self.find_element("xpath", xpath).click()
                return
            except:
                time.sleep(freq)

    def implicitly_wait(self, timeout=20.0, freq=0.5):
        self._wait = WebDriverWait(self, timeout=timeout, poll_frequency=freq)

    def wait(
        self,
        secs: float = 0.0,
        *,
        key: str | None = None,
        keys: list[tuple[str, Callable]] | None = None,
        realtime: str | None = None,
        durtime: tuple[str, str] | None = None,
        timeformat: str | None = None,
    ):
        """
        timeformat 쓰는법
        12:30:52 "%H:%M:%S"
        12:30:52.213 "%H:%M:%S.%f"
        12시 30분 52초 "%H시 %M분 %S초"

        """
        if secs:
            time.sleep(secs)
        elif key:
            if keys:
                ls = []
                for k, f in keys:
                    ls.append(keyboard.add_hotkey(k, f))
            keyboard.wait(key)
            if keys:
                for f in ls:
                    keyboard.remove_hotkey(f)

        elif timeformat:
            if realtime:
                target_time = datetime.strptime(realtime, timeformat)
                now = datetime.now()
                target_time = now.replace(
                    hour=target_time.hour,
                    minute=target_time.minute,
                    second=target_time.second,
                    microsecond=target_time.microsecond,
                )

                if target_time < now:
                    target_time += timedelta(days=1)

                # 목표 시각까지 남은 시간을 계산
                time_to_wait = (target_time - now).total_seconds()

                if time_to_wait > 0:
                    time.sleep(time_to_wait)

            elif durtime:
                time1 = datetime.strptime(durtime[0], timeformat)
                time2 = datetime.strptime(durtime[1], timeformat)
                time_to_wait = abs((time2 - time1).total_seconds())
                time.sleep(time_to_wait)

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
        -1 가능.
        """
        if i >= len(self.window_handles):
            self.wait().until(EC.number_of_windows_to_be(i + 1))
        self.switch_to.window(self.window_handles[i])

    def goto_alert(self):
        self.wait().until(EC.alert_is_present())
        return self.switch_to.alert

    def goto_focused_element(self):
        return Element(self.switch_to.active_element)
