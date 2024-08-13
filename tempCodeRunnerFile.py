
web.find(title="비밀번호 입력").send_keys(pw + "\n")

web.uncertain(lambda: web.find(id="sapSL_DEFAULT_BUTTON").click())