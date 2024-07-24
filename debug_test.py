from models.core import ChromeDriver
from models.debugger import debugger
from utils import get_xpath

debugger.run(__file__)

driver = ChromeDriver()

driver.get("https://www.google.com")
driver.wait(10)
driver.find(text="temp").send_keys("Hello, World!")

debugger.close()
