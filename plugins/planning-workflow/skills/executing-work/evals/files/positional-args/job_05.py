from client import fetch

EXAMPLE = "fetch(url, 5)"


def run_5(url, limit):
    # fetch(url, 5) stays in this comment
    first = fetch(url, 50)
    second = fetch(url, timeout=limit)
    third = fetch(url, limit * 5)
    return first, second, third, fetch(url, limit + 5)
