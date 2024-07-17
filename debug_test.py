from models.core import ChromeDriver
from models.debugger import debugger
from utils import get_xpath

debugger.run(__file__)

driver = ChromeDriver()

driver.get("https://www.google.com")
print(get_xpath(title="검색"))
driver.find(title="검색").send_keys("Hello, World\n")
driver.wait(10)
print(driver.find(text_contains="최애의").text)
debugger.close()
