import keyboard
from models.core import ChromeDriver
from models.debugger import debugger
from utils import get_xpath

debugger.run(__file__)

driver = ChromeDriver()

driver.get("https://www.google.com")

driver.implicitly_wait(3)
keyboard.wait("esc")

for i, window in enumerate(driver.window_handles):
    print(f"Window {i}: {window}")
    driver.switch_to.window(window)
    print(driver.find(get_xpath(title="검색")))
