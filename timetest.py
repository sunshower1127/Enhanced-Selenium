from datetime import datetime
from models.core.driver import ChromeDriver
from models.debugger import debugger
from utils import get_idpw

debugger.run(__file__)

es = ChromeDriver()

es.get("https://hana-prd-ap-4.ssu.ac.kr:8443/zu4a/zcmui2245")
id, pw = get_idpw()
es.find(title="아이디 입력").send_keys(id)
es.find(title="비밀번호 입력").send_keys(pw + "\n")

es.uncertain(lambda: es.find(id="sapSL_DEFAULT_BUTTON").click())

# 여기까지가 로그인하는 부분.

while True:
    es.wait(key="q")
    begin_time = datetime.now()
    es.refresh()
    # 이 아래에서 시간 찾는 코드 작성해야함.
    t = es.find().text
    end_time = datetime.strptime(t, "%H:%M:%S")
    print(f"{begin_time=}\n{end_time=}")


debugger.close()
