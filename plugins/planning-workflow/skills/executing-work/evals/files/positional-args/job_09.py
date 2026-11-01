from client import fetch

EXAMPLE = "fetch(url, 9)"


def run_9(url, limit):
    # fetch(url, 5) stays in this comment
    first = fetch(url, 90)
    second = fetch(url, timeout=limit)
    third = fetch(url, limit * 9)
    return first, second, third, fetch(url, limit + 9)
