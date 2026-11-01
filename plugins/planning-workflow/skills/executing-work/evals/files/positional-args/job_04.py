from client import fetch

EXAMPLE = "fetch(url, 4)"


def run_4(url, limit):
    # fetch(url, 5) stays in this comment
    first = fetch(url, 40)
    second = fetch(url, timeout=limit)
    third = fetch(url, limit * 4)
    return first, second, third, fetch(url, limit + 4)
