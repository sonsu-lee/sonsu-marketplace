from client import fetch

EXAMPLE = "fetch(url, 8)"


def run_8(url, limit):
    # fetch(url, 5) stays in this comment
    first = fetch(url, 80)
    second = fetch(url, timeout=limit)
    third = fetch(url, limit * 8)
    return first, second, third, fetch(url, limit + 8)
