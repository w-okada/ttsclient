import socketio

from ttsclient.server.tts_server_socketio_namespace import SocketIONamespace


class SocketIOServer(socketio.AsyncServer):
    _instance: socketio.AsyncServer | None = None

    @classmethod
    def get_instance(
        cls,
        allowed_origins: list[str] | None = None,
    ):
        if cls._instance is None:
            # sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
            if allowed_origins is None:
                sio = cls(async_mode="asgi")
            else:
                sio = cls(async_mode="asgi", cors_allowed_origins=allowed_origins)
            # sio = cls(async_mode="asgi", cors_allowed_origins="*")
            cls._instance = sio
            namespace = SocketIONamespace.get_instance(cls._instance.list_all_sids)
            sio.register_namespace(namespace)
            return cls._instance

        return cls._instance

    def list_all_sids(self, namespace="/", room=None):
        return [sid for sid in self.manager.get_participants(namespace, room=room)]
