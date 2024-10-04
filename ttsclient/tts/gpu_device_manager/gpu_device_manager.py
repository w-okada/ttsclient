import logging
import platform
import re
import torch

from ...const import LOGGER_NAME
from ..data_types.data_types import GPUInfo


def reload_gpu_info_for_win() -> list[GPUInfo]:
    import clr

    clr.AddReference("System.Management")
    from System.Management import ManagementObjectSearcher  # type: ignore

    management_objects = ManagementObjectSearcher("select * from Win32_VideoController")
    gpu_info: list[GPUInfo] = []
    gpu_info.append(GPUInfo(name="cpu", device_id="-1", adapter_ram=0, device_id_int=-1))
    for management_object in management_objects.Get():
        name = management_object["Name"]
        device_id = management_object["DeviceID"]
        try:
            logging.getLogger(LOGGER_NAME).info(f"AdapterRAM : {management_object['AdapterRAM']}")
            if management_object["AdapterRAM"] is not None:
                adapter_ram = int(management_object["AdapterRAM"])
            else:
                adapter_ram = 0
        except Exception as e:
            logging.getLogger(LOGGER_NAME).error(f"AdapterRAM is not found. {e}")
            adapter_ram = 0

        try:
            device_id_int = int(re.findall(r"\d+", device_id)[0]) - 1
        except Exception as e:
            logging.getLogger(LOGGER_NAME).error(f"DeviceID is not found.(1) {e} ")
            logging.getLogger(LOGGER_NAME).error(f"DeviceID is not found.(2) {device_id} ")
            device_id_int = -1

        gpu_info.append(GPUInfo(name=name, device_id=device_id, adapter_ram=adapter_ram, device_id_int=device_id_int))

    management_objects.Dispose()
    return gpu_info


def reload_gpu_info() -> list[GPUInfo]:
    if platform.system() == "Windows":
        try:
            return reload_gpu_info_for_win()
        except Exception as e:
            logging.getLogger(LOGGER_NAME).error(f"Failed to reload_gpu_info_for_win. {e}. If you are using torch_cuda, this error can be ignored.")
            gpu_info: list[GPUInfo] = []
            gpu_info.append(GPUInfo(name="cpu", device_id="-1", adapter_ram=0, device_id_int=-1))
            return gpu_info
    elif platform.system() == "Linux":
        gpu_info = []
        gpu_info.append(GPUInfo(name="cpu", device_id="-1", adapter_ram=0, device_id_int=-1))
        return gpu_info
    elif platform.system() == "Darwin":
        gpu_info = []
        gpu_info.append(GPUInfo(name="cpu", device_id="-1", adapter_ram=0, device_id_int=-1))
        return gpu_info
    else:
        logging.getLogger(LOGGER_NAME).error(f"Unknown platform:{platform.system()}")
        gpu_info = []
        gpu_info.append(GPUInfo(name="cpu", device_id="-1", adapter_ram=0, device_id_int=-1))
        return gpu_info


def reload_cuda_info() -> list[GPUInfo]:
    gpu_info = []
    gpu_info.append(GPUInfo(name="cpu", device_id="-1", adapter_ram=0, device_id_int=-1))
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            gpu_info.append(
                GPUInfo(
                    name=torch.cuda.get_device_name(i),
                    device_id=str(i),
                    adapter_ram=torch.cuda.get_device_properties(i).total_memory,
                    device_id_int=i,
                    cuda_compute_version_major=torch.cuda.get_device_properties(i).major,
                    cuda_compute_version_minor=torch.cuda.get_device_properties(i).minor,
                )
            )

    return gpu_info


def get_cuda_version():
    import subprocess

    cuda_version = None
    try:
        result = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode("utf-8")
        for line in output.split("\n"):
            logging.getLogger(LOGGER_NAME).info(line)
            if "CUDA Version" in line:
                cuda_version = line.split(":")[-1].strip()
    except Exception as e:
        logging.getLogger(LOGGER_NAME).error(f"Get CUDA version failed. {e}")
    return cuda_version


class GPUDeviceManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:

            cls._instance = cls()
            return cls._instance

        return cls._instance

    def __init__(self):
        self.reload()

    def reload(self):
        logging.getLogger(LOGGER_NAME).info("Reloading GPU info")

        self.gpu_info = reload_gpu_info()
        logging.getLogger(LOGGER_NAME).info(f"GPU[sys]:{self.gpu_info}")

        self.cuda_available = torch.cuda.is_available()
        self.cuda_version = torch.version.cuda
        self.cudnn_version = torch.backends.cudnn.version()
        self.cuda_gpu_num = torch.cuda.device_count()
        self.cuda_mps_enabled = getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available()
        self.cuda_driver_version = get_cuda_version()
        self.cuda_info = reload_cuda_info()
        logging.getLogger(LOGGER_NAME).info(f"GPU[cuda](1): available:{self.cuda_available}, num:{self.cuda_gpu_num}, mps_enabled: {self.cuda_mps_enabled}")
        logging.getLogger(LOGGER_NAME).info(f"GPU[cuda](2): cuda_version(build):{self.cuda_version}, cudnn_version(build){self.cudnn_version}")
        logging.getLogger(LOGGER_NAME).info(f"GPU[cuda](3): cuda_driver_version:{self.cuda_driver_version}")
        logging.getLogger(LOGGER_NAME).info(f"GPU[cuda](4): {self.cuda_info }")

        return self.gpu_info

    def get_gpu_info(self):
        return self.gpu_info

    def get_cuda_info(self):
        return self.cuda_info

    def is_cuda_available(self):
        return self.cuda_available
