# import numpy as np
# import cv2 as cv
# from pytesseract import image_to_string
from __future__ import annotations

from datetime import datetime
from typing import Literal


# 테스트 통과
def get_xpath(
    axis: Literal[
        "ancestor",
        "ancestor-or-self",
        "child",
        "descendant",
        "descendant-or-self",
        "following",
        "following-sibling",
        "parent",
        "preceding",
        "preceding-sibling",
    ] = "descendant",
    tag="*",
    id: str | list[str] | None = None,
    name: str | list[str] | None = None,
    css_class: str | list[str] | None = None,
    css_class_contains: str | list[str] | None = None,
    text: str | list[str] | None = None,
    text_contains: str | list[str] | None = None,
    text_not: str | list[str] | None = None,
    text_not_contains: str | list[str] | None = None,
):
    def ensure_list(value):
        return [value] if isinstance(value, str) else value

    id = ensure_list(id)  # noqa: A001
    name = ensure_list(name)
    css_class = ensure_list(css_class)
    css_class_contains = ensure_list(css_class_contains)
    text = ensure_list(text)
    text_contains = ensure_list(text_contains)
    text_not = ensure_list(text_not)
    text_not_contains = ensure_list(text_not_contains)

    xpath = axis + "::" + tag

    args: list[list[str]] = []
    if id is not None:
        args.append([f"@id='{x}'" for x in id])
    if name is not None:
        args.append([f"@name='{x}'" for x in name])
    if css_class is not None:
        args.append([f"@class='{x}'" for x in css_class])
    if css_class_contains is not None:
        args.append([f"contains(@class, '{x}')" for x in css_class_contains])
    if text is not None:
        args.append([f"text()='{x}'" for x in text])
    if text_contains is not None:
        args.append([f"contains(text(), '{x}')" for x in text_contains])
    if text_not is not None:
        args.append([f"not(text()='{x}')" for x in text_not])
    if text_not_contains is not None:
        args.append([f"not(contains(text(), '{x}'))" for x in text_not_contains])

    xpath += ("{}" if len(args) == 0 else "[{}]").format(
        " and ".join(
            ("{}" if len(arg) == 1 else "({})").format(" or ".join(arg)) for arg in args
        )
    )

    return xpath


def get_total_secs(time_str: str):
    total_seconds = 0
    if "시간" in time_str:
        parsed_time = datetime.strptime(time_str, "%H시간 %M분 %S초").astimezone()
        total_seconds = (
            parsed_time.hour * 3600 + parsed_time.minute * 60 + parsed_time.second
        )
    elif "분" in time_str:
        parsed_time = datetime.strptime(time_str, "%M분 %S초").astimezone()
        total_seconds = parsed_time.minute * 60 + parsed_time.second
    else:
        parsed_time = datetime.strptime(time_str, "%S초").astimezone()
        total_seconds = parsed_time.second
    return total_seconds


def get_idpw(path="idpw.txt", encoding="utf-8"):
    with open(path, encoding=encoding) as file:
        id = file.readline().strip()  # noqa: A001
        pw = file.readline().strip()
    return id, pw


# def solve_captcha(captcha_img: bytes) -> str:
#     """
#     주어진 캡챠 이미지를 해석하여 문자열로 반환합니다.

#     :param captcha_img: 캡챠 이미지의 바이트 데이터
#     :return: 캡챠 이미지에서 추출한 문자열
#     """
#     image_array = np.frombuffer(captcha_img, dtype=np.uint8)
#     image = cv.imdecode(image_array, cv.IMREAD_COLOR)
#     image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
#     image = cv.adaptiveThreshold(
#         image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 91, 1
#     )
#     kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
#     image = cv.morphologyEx(image, cv.MORPH_OPEN, kernel, iterations=1)
#     cnts, _ = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
#     cnts = cnts[0] if len(cnts) == 2 else cnts[1]
#     for c in cnts:
#         area = cv.contourArea(c)
#         if area < 50:
#             cv.drawContours(image, [c], -1, (0, 0, 0), -1)
#     kernel2 = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
#     image = cv.filter2D(image, -1, kernel2)
#     result = 255 - image

#     return image_to_string(result)
