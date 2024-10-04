import logging
import socketio
import asyncio

from ttsclient.const import LOGGER_NAME
from ttsclient.server.event_emitter import EventEmitter
from ttsclient.server.event_emitter_manager import EventEmitterManager


class SocketIONamespace(socketio.AsyncNamespace, EventEmitter):
    sid: int = 0

    async def emit_to(self, event, data, to):
        await self.emit(event, data, to=to)

    def emit_coroutine(self, event, data, to=None):
        if to is None:
            asyncio.run(self.emit_to(event, data, to=None))
        else:
            asyncio.run(self.emit_to(event, data, to=to))

    def __init__(self, namespace: str):
        super().__init__(namespace)
        self.namespace = namespace
        EventEmitterManager.get_instance().set_event_emitter(self)

    @classmethod
    def get_instance(cls, list_all_sids):
        if not hasattr(cls, "_instance"):
            cls._instance = cls("/test")
            cls._instance.list_all_sids = list_all_sids
        return cls._instance

    def on_connect(self, sid, environ):
        self.sid = sid
        logging.getLogger(LOGGER_NAME).info(f"connect sid: {sid}")
        # print("[{}] connet sid : {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sid))
        pass

    async def on_request_message(self, sid, msg):
        pass

    def on_disconnect(self, sid):
        # print('[{}] disconnect'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        pass
