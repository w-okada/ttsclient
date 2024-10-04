import socket


def resolve_base_url(https: bool, port: int):
    if https is False:
        base_url = f"http://localhost:{port}"
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        hostname = s.getsockname()[0]

        base_url = f"https://{hostname}:{port}"
    return base_url
