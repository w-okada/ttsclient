from ttsclient.models.gpu_device import GPUInfo


class GPUDeviceManager:
    _instance: "GPUDeviceManager | None" = None

    def __init__(self) -> None:
        self._gpu_infos: list[GPUInfo] = []

    @classmethod
    def get_instance(cls) -> "GPUDeviceManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload(self) -> list[GPUInfo]:
        # TODO: GPU 検出ロジック
        self._gpu_infos = []
        return self._gpu_infos

    def get_gpu_info(self) -> list[GPUInfo]:
        return self._gpu_infos

    def is_cuda_available(self) -> bool:
        # TODO: CUDA 利用可否判定
        return False
