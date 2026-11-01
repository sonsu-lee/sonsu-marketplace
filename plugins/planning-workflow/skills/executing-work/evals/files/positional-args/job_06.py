from client import fetch

EXAMPLE = "fetch(url, 6)"


def run_6(url, limit):
    # fetch(url, 5) stays in this comment
    first = fetch(url, 60)
    second = fetch(url, timeout=limit)
    third = fetch(url, limit * 6)
    return first, second, third, fetch(url, limit + 6)
