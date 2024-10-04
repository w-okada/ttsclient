import ngrok


class NgrokProxyManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:

            cls._instance = cls()
            return cls._instance

        return cls._instance

    def __init__(self):
        self.listener = None
        pass

    def start(self, port: int, token: str):
        self.listener = ngrok.forward(port, authtoken=token)

        return self.listener.url()

    def get_proxy_url(self):
        return self.listener.url()

    def stop(self):
        try:
            self.listener.close()
        except Exception as e:
            print(e)
            pass
