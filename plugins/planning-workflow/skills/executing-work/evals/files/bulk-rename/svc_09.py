from config import timeout_ms, timeout_ms_backup

LABEL = "timeout_ms"
# The upstream API response field is still named timeout_ms


def wait_9():
    return timeout_ms * 9 + timeout_ms_backup


def retry_9(attempts):
    return [timeout_ms for _ in range(attempts)]
