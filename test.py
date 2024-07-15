from contextlib import suppress

List = []
for i in range(10):
    with suppress(Exception):
        List.append(10 / i)

print(List)
