from models.core import ChromeDriver
from models.debugger import debugger
from utils import get_xpath

debugger.run(__file__)

driver = ChromeDriver()

driver.get("https://www.google.com")
driver.wait(10)
print(get_xpath(title="검색"))
driver._debug_find(get_xpath(title="검색"))

"""





"""
