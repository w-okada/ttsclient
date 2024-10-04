from abc import ABC, abstractmethod
from ttsclient.const import CutMethod


class Pipeline(ABC):

    def __init__(self, gpu_device_id=None):
        self.gpu_device_id = gpu_device_id

    @abstractmethod
    def force_stop(self):
        pass

    @abstractmethod
    def run(
        self,
        ref_wav_path: str,
        prompt_text: str,
        prompt_language: str,
        text: str,
        text_language: str,
        how_to_cut: CutMethod = "No slice",
        top_k: int = 20,
        top_p: float = 1,
        temperature: float = 1,
        speed: float = 1,
        inp_refs: list[str] = [],
        # ここからfasterの追加オプション
        batch_size: int = 1,
        batch_threshold: float = 0.75,
        split_bucket: bool = True,
        return_fragment: bool = False,
        fragment_interval: float = 0.3,
        seed: int = -1,
        parallel_infer: bool = True,
        repetition_penalty: float = 1.35,
    ):
        pass
