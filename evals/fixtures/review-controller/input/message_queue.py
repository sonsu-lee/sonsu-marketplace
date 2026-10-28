def flush(queue, send):
    while queue:
        message = queue.pop(0)
        send(message)
