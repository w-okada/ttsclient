class AppStatus:
    # シングルトン
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            return cls._instance

        return cls._instance

    def __init__(self):
        self.end_flag = False

    def stop_app(self):
        self.end_flag = True
