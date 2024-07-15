from models.chrome_driver import ChromeDriver
from models.debugger import debugger

debugger.run(__file__)

driver = ChromeDriver()

debugger.close()
