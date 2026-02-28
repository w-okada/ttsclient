import logging
import platform
import re

from ttsclient.models.gpu_device import GPUInfo

logger = logging.getLogger(__name__)

_CPU_ENTRY = GPUInfo(name="cpu", device_id="-1", adapter_ram=0, device_id_int=-1)


class GPUDeviceManager:
    _instance: "GPUDeviceManager | None" = None

    def __init__(self) -> None:
        self._gpu_infos: list[GPUInfo] = []
        self._cuda_available = False

    @classmethod
    def get_instance(cls) -> "GPUDeviceManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload(self) -> list[GPUInfo]:
        self._gpu_infos = [_CPU_ENTRY]
        self._cuda_available = False

        cuda_infos = self._reload_cuda_info()
        if cuda_infos:
            self._cuda_available = True
            self._gpu_infos = [_CPU_ENTRY, *cuda_infos]
        elif platform.system() == "Windows":
            win_infos = self._reload_gpu_info_win()
            if win_infos:
                self._gpu_infos = [_CPU_ENTRY, *win_infos]

        logger.info("GPU デバイス検出: %d 件 (CUDA: %s)", len(self._gpu_infos), self._cuda_available)
        return self._gpu_infos

    def get_gpu_info(self) -> list[GPUInfo]:
        return self._gpu_infos

    def is_cuda_available(self) -> bool:
        return self._cuda_available

    def _reload_cuda_info(self) -> list[GPUInfo]:
        try:
            import torch
        except ImportError:
            logger.info("torch が見つかりません。CUDA 検出をスキップします")
            return []

        if not torch.cuda.is_available():
            return []

        infos: list[GPUInfo] = []
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            infos.append(
                GPUInfo(
                    name=torch.cuda.get_device_name(i),
                    device_id=str(i),
                    adapter_ram=props.total_memory,
                    device_id_int=i,
                    cuda_compute_version_major=props.major,
                    cuda_compute_version_minor=props.minor,
                )
            )
        logger.info("CUDA GPU 検出: %d 件", len(infos))
        return infos

    def _reload_gpu_info_win(self) -> list[GPUInfo]:
        try:
            import clr  # type: ignore[import-untyped]

            clr.AddReference("System.Management")
            from System.Management import ManagementObjectSearcher  # type: ignore[import-untyped]
        except ImportError:
            return []

        infos: list[GPUInfo] = []
        try:
            searcher = ManagementObjectSearcher("select * from Win32_VideoController")
            for obj in searcher.Get():
                name = obj["Name"] or ""
                device_id = obj["DeviceID"] or ""

                try:
                    adapter_ram = int(obj["AdapterRAM"]) if obj["AdapterRAM"] is not None else 0
                except Exception:
                    adapter_ram = 0

                try:
                    device_id_int = int(re.findall(r"\d+", device_id)[0]) - 1
                except Exception:
                    device_id_int = -1

                infos.append(GPUInfo(name=name, device_id=device_id, adapter_ram=adapter_ram, device_id_int=device_id_int))
            searcher.Dispose()
        except Exception:
            logger.warning("Windows GPU 情報の取得に失敗しました", exc_info=True)

        return infos
