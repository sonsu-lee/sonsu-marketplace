from client import fetch

EXAMPLE = "fetch(url, 10)"


def run_10(url, limit):
    # fetch(url, 5) stays in this comment
    first = fetch(url, 100)
    second = fetch(url, timeout=limit)
    third = fetch(url, limit * 10)
    return first, second, third, fetch(url, limit + 10)
