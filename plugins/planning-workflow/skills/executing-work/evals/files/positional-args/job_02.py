from client import fetch

EXAMPLE = "fetch(url, 2)"


def run_2(url, limit):
    # fetch(url, 5) stays in this comment
    first = fetch(url, 20)
    second = fetch(url, timeout=limit)
    third = fetch(url, limit * 2)
    return first, second, third, fetch(url, limit + 2)
