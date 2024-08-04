from models.core.driver import ChromeDriver
from models.debugger import debugger
from utils import get_idpw
from models.core.findable_element import Elements

debugger.run(__file__)

web = ChromeDriver()
web.set_window_size(1920 // 2, 1080)
web.implicitly_wait(3, 0.01)
web.get("https://hana-prd-ap-4.ssu.ac.kr:8443/zu4a/zcmui2245")
id, pw = get_idpw()
web.find(title="아이디 입력").send_keys(id)
web.find(title="비밀번호 입력").send_keys(pw + "\n")

web.uncertain(lambda: web.find(id="sapSL_DEFAULT_BUTTON").click())

# 아래 realtime을 timetest.py에서 뽑아내야함. 일단 0.4초는 통과고, 0.2초 도전해보자.
web.wait(realtime="00:56:00.05", timeformat="%H:%M:%S.%f")
web.refresh()

idx = 1


# 신청 버튼
def handle_q():
    global idx
    print("강의신청")
    web.uncertain(lambda: web.find(id=f"__button6-__clone{idx}").click())


# 다음 강의 버튼
def handle_w():
    global idx
    n = int(input("강의번호: "))
    idx = 1 + (n - 1) * 13


# 자동으로 가장 많은 강의 신청
def handle_e():
    try:
        btns = web.find_all(id_contains="__button6-__clone")
        cur_people = list(map(int, btns.find().texts))
        max_people = list(map(int, btns.find().texts))
        max(list(zip(btns, cur_people, max_people)), key=lambda x: x[1] / x[2])[
            0
        ].click()

    except:
        print("e 실패.")


web.implicitly_wait(30, 0.01)

# 첫번째 강의만 자동으로 잡고,
web.uncertain(lambda: web.find(id="__button6-__clone1"))
print("done")
web.wait(key="q")

# 수동방식 : q누르면 수강신청, w누르면 강의 번호 변경
# 자동방식 : e누르면 현재수강인원/최대수강인원이 가장 높은 강의를 신청
web.wait(key="esc", keys=[("q", handle_q), ("w", handle_w), ("e", handle_e)])


debugger.close()
