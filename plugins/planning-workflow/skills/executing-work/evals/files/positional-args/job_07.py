from client import fetch

EXAMPLE = "fetch(url, 7)"


def run_7(url, limit):
    # fetch(url, 5) stays in this comment
    first = fetch(url, 70)
    second = fetch(url, timeout=limit)
    third = fetch(url, limit * 7)
    return first, second, third, fetch(url, limit + 7)
