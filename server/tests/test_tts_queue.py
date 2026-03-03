"""TTSQueue の deadline 優先度・直列実行・初回セグメント遅延のテスト。

TTSManager.run() をモックし、キューの並び替え・直列実行の振る舞いを検証する。
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import patch

import numpy as np
import pytest

from ttsclient.models.tts import GenerateVoiceParam
from ttsclient.services.tts_queue import TTSQueue


def _make_param(text: str = "hello", deadline: float | None = None) -> GenerateVoiceParam:
    return GenerateVoiceParam(
        voice_character_slot_index=0,
        reference_voice_slot_index=0,
        text=text,
        language="all_ja",
        speed=1.0,
        deadline=deadline,
    )


@pytest.fixture()
def _reset_queue():
    """各テストで TTSQueue シングルトンをリセットする。"""
    TTSQueue._instance = None
    yield
    TTSQueue._instance = None


# ---------------------------------------------------------------------------
# TestDeadlineOrdering
# ---------------------------------------------------------------------------


class TestDeadlineOrdering:
    """worker 処理中にキューに溜まったアイテムが deadline 昇順で処理されることを検証。"""

    @pytest.mark.usefixtures("_reset_queue")
    def test_lower_deadline_first(self):
        """小さい deadline のアイテムが先に処理される。"""
        processed: list[str] = []

        def mock_run(param: GenerateVoiceParam) -> tuple[int, np.ndarray]:
            processed.append(param.text)
            if param.text == "blocker":
                time.sleep(0.1)  # worker をブロックして他のアイテムをキューに積ませる
            return (22050, np.zeros(100, dtype=np.int16))

        async def run_test():
            queue = TTSQueue.get_instance()
            loop = asyncio.get_running_loop()
            queue.start(loop)

            with patch("ttsclient.services.tts_queue.TTSManager") as mock_cls:
                mock_cls.get_instance.return_value.run = mock_run

                # blocker を先に submit → worker が処理中の間に他をキューに積む
                blocker = asyncio.create_task(queue.submit(_make_param("blocker", deadline=0)))
                await asyncio.sleep(0.01)  # worker が blocker を取り出すのを待つ

                # deadline: 遠い → 近い順に submit
                t3 = asyncio.create_task(queue.submit(_make_param("C", deadline=300)))
                t1 = asyncio.create_task(queue.submit(_make_param("A", deadline=100)))
                t2 = asyncio.create_task(queue.submit(_make_param("B", deadline=200)))

                await asyncio.gather(blocker, t1, t2, t3)

            await queue.stop()
            # blocker の後は deadline 昇順
            assert processed == ["blocker", "A", "B", "C"]

        asyncio.run(run_test())

    @pytest.mark.usefixtures("_reset_queue")
    def test_same_deadline_fifo(self):
        """同一 deadline なら submit 順 (sequence) で処理される。"""
        processed: list[str] = []

        def mock_run(param: GenerateVoiceParam) -> tuple[int, np.ndarray]:
            processed.append(param.text)
            if param.text == "blocker":
                time.sleep(0.1)
            return (22050, np.zeros(100, dtype=np.int16))

        async def run_test():
            queue = TTSQueue.get_instance()
            loop = asyncio.get_running_loop()
            queue.start(loop)

            with patch("ttsclient.services.tts_queue.TTSManager") as mock_cls:
                mock_cls.get_instance.return_value.run = mock_run

                blocker = asyncio.create_task(queue.submit(_make_param("blocker", deadline=0)))
                await asyncio.sleep(0.01)

                t1 = asyncio.create_task(queue.submit(_make_param("first", deadline=100)))
                t2 = asyncio.create_task(queue.submit(_make_param("second", deadline=100)))
                t3 = asyncio.create_task(queue.submit(_make_param("third", deadline=100)))

                await asyncio.gather(blocker, t1, t2, t3)

            await queue.stop()
            assert processed == ["blocker", "first", "second", "third"]

        asyncio.run(run_test())

    @pytest.mark.usefixtures("_reset_queue")
    def test_none_is_immediate(self):
        """deadline=None は time.time() 扱い。遠い未来 deadline より先に処理される。"""
        processed: list[str] = []

        def mock_run(param: GenerateVoiceParam) -> tuple[int, np.ndarray]:
            processed.append(param.text)
            if param.text == "blocker":
                time.sleep(0.1)
            return (22050, np.zeros(100, dtype=np.int16))

        async def run_test():
            queue = TTSQueue.get_instance()
            loop = asyncio.get_running_loop()
            queue.start(loop)

            with patch("ttsclient.services.tts_queue.TTSManager") as mock_cls:
                mock_cls.get_instance.return_value.run = mock_run

                blocker = asyncio.create_task(queue.submit(_make_param("blocker", deadline=0)))
                await asyncio.sleep(0.01)

                # 遠い未来の deadline を先に submit
                far_future = asyncio.create_task(
                    queue.submit(_make_param("far_future", deadline=time.time() + 9999))
                )
                # None (= 即時) を後に submit
                immediate = asyncio.create_task(queue.submit(_make_param("immediate", deadline=None)))

                await asyncio.gather(blocker, far_future, immediate)

            await queue.stop()
            assert processed == ["blocker", "immediate", "far_future"]

        asyncio.run(run_test())


# ---------------------------------------------------------------------------
# TestSerialExecution
# ---------------------------------------------------------------------------


class TestSerialExecution:
    """各アイテムの処理が重ならず直列に実行されることを検証。"""

    @pytest.mark.usefixtures("_reset_queue")
    def test_no_concurrent_execution(self):
        """各アイテムの (start, end) タイムスタンプが重ならない。"""
        timestamps: list[tuple[float, float]] = []

        def mock_run(param: GenerateVoiceParam) -> tuple[int, np.ndarray]:
            start = time.monotonic()
            time.sleep(0.05)
            end = time.monotonic()
            timestamps.append((start, end))
            return (22050, np.zeros(100, dtype=np.int16))

        async def run_test():
            queue = TTSQueue.get_instance()
            loop = asyncio.get_running_loop()
            queue.start(loop)

            with patch("ttsclient.services.tts_queue.TTSManager") as mock_cls:
                mock_cls.get_instance.return_value.run = mock_run

                tasks = [
                    asyncio.create_task(queue.submit(_make_param(f"item_{i}", deadline=float(i))))
                    for i in range(3)
                ]
                await asyncio.gather(*tasks)

            await queue.stop()

            assert len(timestamps) == 3
            # 各アイテムの start が前のアイテムの end 以降であること
            for i in range(1, len(timestamps)):
                assert timestamps[i][0] >= timestamps[i - 1][1], (
                    f"Item {i} started at {timestamps[i][0]} "
                    f"before item {i-1} ended at {timestamps[i-1][1]}"
                )

        asyncio.run(run_test())

    @pytest.mark.usefixtures("_reset_queue")
    def test_result_to_correct_caller(self):
        """各 submit() が自分のリクエスト結果を受け取る。"""

        def mock_run(param: GenerateVoiceParam) -> tuple[int, np.ndarray]:
            # text をもとにユニークな audio を生成
            marker = len(param.text)
            return (22050, np.full(marker, marker, dtype=np.int16))

        async def run_test():
            queue = TTSQueue.get_instance()
            loop = asyncio.get_running_loop()
            queue.start(loop)

            with patch("ttsclient.services.tts_queue.TTSManager") as mock_cls:
                mock_cls.get_instance.return_value.run = mock_run

                texts = ["a", "bb", "ccc"]
                tasks = [
                    asyncio.create_task(queue.submit(_make_param(t, deadline=float(i))))
                    for i, t in enumerate(texts)
                ]
                results = await asyncio.gather(*tasks)

            await queue.stop()

            for text, (sr, audio) in zip(texts, results):
                expected_len = len(text)
                assert sr == 22050
                assert len(audio) == expected_len
                assert audio[0] == expected_len

        asyncio.run(run_test())


# ---------------------------------------------------------------------------
# TestFirstSegmentLatency
# ---------------------------------------------------------------------------


class TestFirstSegmentLatency:
    """最初のセグメント (最小 deadline) の完了レイテンシが処理時間 + α 以内。"""

    @pytest.mark.usefixtures("_reset_queue")
    def test_not_blocked_by_later(self):
        """最小 deadline のアイテムが後続に阻まれず即座に処理される。"""
        processing_time = 0.05

        def mock_run(param: GenerateVoiceParam) -> tuple[int, np.ndarray]:
            time.sleep(processing_time)
            return (22050, np.zeros(100, dtype=np.int16))

        async def run_test():
            queue = TTSQueue.get_instance()
            loop = asyncio.get_running_loop()
            queue.start(loop)

            with patch("ttsclient.services.tts_queue.TTSManager") as mock_cls:
                mock_cls.get_instance.return_value.run = mock_run

                # 先に遠い deadline のアイテムを複数 submit
                later_tasks = [
                    asyncio.create_task(queue.submit(_make_param(f"later_{i}", deadline=9999 + i)))
                    for i in range(3)
                ]
                await asyncio.sleep(0)  # イベントループに1回制御を返す

                # 最小 deadline のアイテムを submit
                start = time.monotonic()
                first_result = await queue.submit(_make_param("first", deadline=0))
                elapsed = time.monotonic() - start

                # 残りをキャンセルせず完了を待つ (patch スコープ内)
                await asyncio.gather(*later_tasks)

            await queue.stop()

            assert first_result[0] == 22050
            # 処理時間 + 50ms 以内に完了すること (スケジューリングオーバーヘッド許容)
            assert elapsed < processing_time + 0.05, (
                f"First segment latency {elapsed:.3f}s exceeded "
                f"expected {processing_time + 0.05:.3f}s"
            )

        asyncio.run(run_test())
