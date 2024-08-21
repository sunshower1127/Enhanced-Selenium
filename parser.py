from pyparsing import (
    QuotedString,
    Suppress,
    Word,
    alphanums,
    infix_notation,
    one_of,
    opAssoc,
)

# Define the grammar
identifier = Word(alphanums + "_-") | QuotedString('"') | QuotedString("'")
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
    prop_name = prop_name.replace("css_class", "class")
    if "text" in prop_name:
        prop_name = prop_name.replace("text", "text()")
    else:
        prop_name = "@" + prop_name

    idx = prop_name.find("_contains")
    if idx != -1:
        prop_name = prop_name[:idx]
        return "contains(" + prop_name + ", '{}')"

    return prop_name + "='{}'"


# Parse the expression
def parse_expression(expression: str, prop_name: str):
    parsed_expression = expr.parse_string(expression, parse_all=True).as_list()[0]
    prop_format = get_prop_format(prop_name)
    logical_expression = convert_to_logical_expression(parsed_expression, prop_format)
    if logical_expression[0] == "(":
        logical_expression = logical_expression[1:]
    if logical_expression[-1] == ")":
        logical_expression = logical_expression[:-1]

    return logical_expression


def convert_to_logical_expression(element: str, prop_format: str) -> str:
    if isinstance(element, list):
        if element[0] == "!" and isinstance(element[1], str):
            element[1] = [element[1]]

        temp = ""
        if element[0] != "!":
            temp += "("

        for sub_element in element:
            temp += convert_to_logical_expression(sub_element, prop_format)

        if element[0] != "!":
            temp += ")"
        return temp

    if element == "|":
        return " or "
    if element == "&":
        return " and "
    if element == "!":
        return "not"

    return prop_format.format(element)


# Test code
if __name__ == "__main__":
    expression = "!A & B | C & D"
    prop_format = "id_contains"
    result = parse_expression(expression, prop_format)
    print(result)
