from client import fetch

EXAMPLE = "fetch(url, 3)"


def run_3(url, limit):
    # fetch(url, 5) stays in this comment
    first = fetch(url, 30)
    second = fetch(url, timeout=limit)
    third = fetch(url, limit * 3)
    return first, second, third, fetch(url, limit + 3)
