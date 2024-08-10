import re

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


# Function to replace operators and add quotes around variables
# def replace() :

#     return result_str


# Parse the expression
def parse(expression: str):
    result = expr.parse_string(expression, parse_all=True)
    return result.as_list()[0]


a = parse("!(d | e) & f")
print(a)


def recur(e, tag):
    if isinstance(e, list):
        if len(e) == 2 and e[0] == "!":
            e[1] = [e[1]]

        temp = "("

        for i in e:
            temp += recur(i, tag)
        temp += ")"
        return temp

    if e == "|":
        return " or "
    if e == "&":
        return " and "
    if e == "!":
        return "not"

    return f"@{tag}='{e}'"


a = recur(a, "id")
print(a)
