import threading


def print_active_threads(tag: str):
    print(f"[{tag}] Active Threads:", threading.enumerate())
