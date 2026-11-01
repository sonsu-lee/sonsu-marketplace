from client import fetch

EXAMPLE = "fetch(url, 1)"


def run_1(url, limit):
    # fetch(url, 5) stays in this comment
    first = fetch(url, 10)
    second = fetch(url, timeout=limit)
    third = fetch(url, limit * 1)
    return first, second, third, fetch(url, limit + 1)
