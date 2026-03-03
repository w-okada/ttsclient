from __future__ import annotations

import asyncio
import heapq
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import numpy as np

from ttsclient.models.tts import GenerateVoiceParam
from ttsclient.services.tts_manager import TTSManager

logger = logging.getLogger(__name__)


@dataclass(order=True)
class QueueItem:
    deadline: float
    sequence: int
    param: GenerateVoiceParam = field(compare=False)
    future: asyncio.Future[tuple[int, np.ndarray]] = field(compare=False)


class TTSQueue:
    _instance: TTSQueue | None = None

    def __init__(self) -> None:
        self._heap: list[QueueItem] = []
        self._sequence = 0
        self._event = asyncio.Event()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._worker_task: asyncio.Task[None] | None = None
        self._running = False
        self._loop: asyncio.AbstractEventLoop | None = None

    @classmethod
    def get_instance(cls) -> TTSQueue:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._running = True
        self._worker_task = loop.create_task(self._worker())
        logger.info("TTSQueue worker started")

    async def stop(self) -> None:
        self._running = False
        self._event.set()
        if self._worker_task is not None:
            await self._worker_task
        self._executor.shutdown(wait=False)
        logger.info("TTSQueue worker stopped")

    async def submit(self, param: GenerateVoiceParam) -> tuple[int, np.ndarray]:
        loop = asyncio.get_running_loop()
        future: asyncio.Future[tuple[int, np.ndarray]] = loop.create_future()

        deadline = param.deadline if param.deadline is not None else time.time()
        item = QueueItem(
            deadline=deadline,
            sequence=self._sequence,
            param=param,
            future=future,
        )
        self._sequence += 1
        heapq.heappush(self._heap, item)
        self._event.set()

        return await future

    async def _worker(self) -> None:
        while self._running:
            if not self._heap:
                self._event.clear()
                await self._event.wait()
                continue

            item = heapq.heappop(self._heap)
            try:
                loop = asyncio.get_running_loop()
                sample_rate, audio_data = await loop.run_in_executor(
                    self._executor,
                    TTSManager.get_instance().run,
                    item.param,
                )
                item.future.set_result((sample_rate, audio_data))
            except Exception as e:
                if not item.future.done():
                    item.future.set_exception(e)
