from fastapi import APIRouter


class RestHello:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route("/api/hello", self.hello, methods=["GET"])

        self.router.add_api_route("/api_hello", self.hello, methods=["GET"])

    def hello(self):
        return {
            "message": "Hello World! TTSClient gives a cute voice to you!",
            "credit": "w-okada",
            "repository": "https://github.com/w-okada/voice-changer",
        }
