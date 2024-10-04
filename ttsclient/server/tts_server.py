import logging
import os
from time import sleep
import uvicorn
import asyncio

import threading
import portpicker
import importlib.util

from ttsclient.const import LOGGER_NAME
from ttsclient.server.key_generator import generate_self_signed_cert
from ttsclient.server.tts_server_socketio_server import SocketIOServer


class TTSServer:
    _instance = None
    port = 0
    server_thread: threading.Thread | None = None

    @classmethod
    def get_instance(
        cls,
        host: str = "127.0.0.1",
        port: int | None = None,
        https: bool = False,
        allow_origins: list[str] | None = None,
    ):
        if cls._instance is None:
            app = TTSServer(host=host, port=port, https=https, allow_origins=allow_origins)
            cls._instance = app
            return cls._instance

        return cls._instance

    # def __init__(self, host: str = "127.0.0.1", port: int | None = None, https: bool = False, allow_origins: list[str] | None = ["*"]):
    def __init__(self, host: str = "127.0.0.1", port: int | None = None, https: bool = False, allow_origins: list[str] | None = None):
        super().__init__()
        self.host = (host,)
        self.https = https
        self.allow_origins = allow_origins

        if port is not None:
            self.port = port
        else:
            self.port = portpicker.pick_unused_port()

    def start(self):
        this_modeule = importlib.util.find_spec(__name__)
        if this_modeule is None:
            raise Exception("FastAPI instance is not initialized.")

        module_parent = this_modeule.parent
        if self.https is True:
            cert, key = generate_self_signed_cert()

            config = uvicorn.Config(
                f"{module_parent}.tts_server_socketio:serverio_app",
                host=self.host,
                port=self.port,
                log_level="info",
                log_config=None,
                ssl_keyfile=key,
                ssl_certfile=cert,
            )
        else:
            config = uvicorn.Config(
                f"{module_parent}.tts_server_socketio:serverio_app",
                host=self.host,
                port=self.port,
                log_level="info",
                log_config=None,
            )

        self.server = uvicorn.Server(config)
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()
        return self.port

    async def stop_all_sockets(self):
        sio = SocketIOServer.get_instance()
        for sid in list(sio.eio.sockets.keys()):
            await sio.disconnect(sid)

    def start_server(self):
        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        logging.getLogger(LOGGER_NAME).info(f"Starting VCServer on port {self.port}")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self.server.serve())
        except Exception as e:
            logging.getLogger(LOGGER_NAME).error(f"VCServer stopped.{e}")
            print(f"VCServer stopped.{e}")
        except asyncio.CancelledError as err:
            logging.getLogger(LOGGER_NAME).error(f"VCServer stopped.{err}")
            print(f"VCServer stopped.{err}")

        # これを呼び出すとpendingエラーが表示される。行儀良くないが、今は呼ばない。
        # self.loop.close()

    def stop(self):

        pending = [t for t in asyncio.all_tasks(self.loop) if not t.done()]
        if pending:
            print(f"There are {len(pending)} pending tasks")
            for task in pending:
                task.cancel()

        self.server.should_exit = True
        sleep(1)
        logging.getLogger(LOGGER_NAME).info("wait vccserver to stop...")
        self.loop.stop()
        self.server_thread.join()
        logging.getLogger(LOGGER_NAME).info("wait vccserver to stop...done")
