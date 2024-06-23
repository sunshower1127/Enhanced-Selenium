import numpy as np
import cv2 as cv
from pytesseract import image_to_string
from datetime import datetime


def get_xpath(
    tag: str = "*",
    id: str | list[str] = None,
    name: str | list[str] = None,
    css_class: str | list[str] = None,
    css_class_contains: str | list[str] = None,
    text: str | list[str] = None,
    text_contains: str | list[str] = None,
    text_not: str | list[str] = None,
    text_not_contains: str | list[str] = None,
):
    isinstance(id, str) and (id := [id])
    isinstance(name, str) and (name := [name])
    isinstance(css_class, str) and (css_class := [css_class])
    isinstance(css_class_contains, str) and (css_class_contains := [css_class_contains])
    isinstance(text, str) and (text := [text])
    isinstance(text_contains, str) and (text_contains := [text_contains])
    isinstance(text_not, str) and (text_not := [text_not])
    isinstance(text_not_contains, str) and (text_not_contains := [text_not_contains])

    xpath = "descendant::" + tag

    args: list[list] = []
    id and args.append([f"@id='{x}'" for x in id])
    name and args.append([f"@name='{x}'" for x in name])
    css_class and args.append([f"@class='{x}'" for x in css_class])
    css_class_contains and args.append(
        [f"contains(@class, '{x}')" for x in css_class_contains]
    )
    text and args.append([f"text()='{x}'" for x in text])
    text_contains and args.append([f"contains(text(), '{x}')" for x in text_contains])
    text_not and args.append([f"not(text()='{x}')" for x in text_not])
    text_not_contains and args.append(
        [f"not(contains(text(), '{x}'))" for x in text_not_contains]
    )

    xpath += ("{}" if len(args) == 1 else "[{}]").format(
        " and ".join(
            ("{}" if len(arg) == 1 else "({})").format(" or ".join(arg)) for arg in args
        )
    )

    return xpath


def get_total_secs(str):
    if "시간" in str:
        return datetime.strptime(str, "%H시간 %M분 %S초").second
    elif "분" in str:
        return datetime.strptime(str, "%M분 %S초").second
    else:
        return datetime.strptime(str, "%S초").second


def get_idpw(path="idpw.txt", encoding="utf-8"):
    with open(path, "r", encoding=encoding) as file:
        id = file.readline().strip()
        pw = file.readline().strip()
    return id, pw


def solve_captcha(captcha_img: bytes) -> str:
    """
    주어진 캡챠 이미지를 해석하여 문자열로 반환합니다.

    :param captcha_img: 캡챠 이미지의 바이트 데이터
    :return: 캡챠 이미지에서 추출한 문자열
    """
    image_array = np.frombuffer(captcha_img, dtype=np.uint8)
    image = cv.imdecode(image_array, cv.IMREAD_COLOR)
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = cv.adaptiveThreshold(
        image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 91, 1
    )
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    image = cv.morphologyEx(image, cv.MORPH_OPEN, kernel, iterations=1)
    cnts, _ = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        area = cv.contourArea(c)
        if area < 50:
            cv.drawContours(image, [c], -1, (0, 0, 0), -1)
    kernel2 = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    image = cv.filter2D(image, -1, kernel2)
    result = 255 - image

    return image_to_string(result)
