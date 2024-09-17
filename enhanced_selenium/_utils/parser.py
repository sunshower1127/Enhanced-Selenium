from __future__ import annotations

from pyparsing import (
    QuotedString,
    Suppress,
    Word,
    infix_notation,
    one_of,
    opAssoc,
    pyparsing_unicode,
)

# Define the grammar
identifier = (
    Word(pyparsing_unicode.alphanums + "_-") | QuotedString('"') | QuotedString("'")
)
operator = one_of("! & |")
lparen = Suppress("(")
rparen = Suppress(")")

# Define the expression using infix_notation
expr = infix_notation(
    identifier,
    [("!", 1, opAssoc.RIGHT), (one_of("& |"), 2, opAssoc.LEFT)],
    lpar=lparen,
    rpar=rparen,
)


def get_prop_format(prop_name: str):
    prop_name = prop_name.replace("class_name", "class")
    if "text" in prop_name:
        prop_name = prop_name.replace("text", "text()")
    else:
        prop_name = "@" + prop_name

    idx = prop_name.find("_contains")
    if idx != -1:
        prop_name = prop_name[:idx]
        return "contains(" + prop_name + ", '{}')"

    return prop_name + "='{}'"


def preprocess_for_not(node: list):
    for i in range(len(node)):
        if isinstance(node[i], list):
            preprocess_for_not(node[i])
        elif i > 0 and node[i - 1] == "!":
            node[i] = [node[i]]


# Parse the expression
def parse_expression(expression: str, prop_name: str):
    parsed_expression = expr.parse_string(expression, parse_all=True).as_list()[0]

    # A -> (A) 로 바꾸기 -> 마지막에 괄호 없애는 과정 통일
    if isinstance(parsed_expression, str):
        parsed_expression = [parsed_expression]

    preprocess_for_not(parsed_expression)

    print(parsed_expression)

    prop_format = get_prop_format(prop_name)
    logical_expression = convert_to_logical_expression(parsed_expression, prop_format)
    if logical_expression[0] == "(":
        logical_expression = logical_expression[1:-1]
    return logical_expression


def convert_to_logical_expression(element: str | list, prop_format: str) -> str:
    if isinstance(element, list):
        result = ""
        if element[0] != "!":
            result += "("

        result += "".join(
            convert_to_logical_expression(sub_element, prop_format)
            for sub_element in element
        )

        if element[0] != "!":
            result += ")"

        return result

    if element == "|":
        return " or "
    if element == "&":
        return " and "
    if element == "!":
        return "not"

    return prop_format.format(element)


"""

!A -> (!A) 인데 이걸 !(A)로 바꾸려고 했고

!(A & B) -> (!(A&B)) 인데 이걸 !(A&B)로 바꾸려고 함.

즉,
!로 시작하는 리스트는 괄호로 안감쌈.

이제 !에서 괄호만 제거하면될거같은데

"""
# Test code
if __name__ == "__main__":
    expression = "!(A & B) | C "
    prop_format = "text"
    result = parse_expression(expression, prop_format)
    print(result)