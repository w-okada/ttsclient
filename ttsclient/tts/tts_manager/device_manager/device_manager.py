import logging
import torch

from ttsclient.tts.gpu_device_manager.gpu_device_manager import GPUDeviceManager

try:
    import torch_directml  # type: ignore

    directml_available = True
except:
    directml_available = False
import onnxruntime


from ....const import LOGGER_NAME


class DeviceManager(object):
    _instance = None
    force_tensor: bool = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if directml_available:
            self.gpu_num = torch_directml.device_count()
        else:
            self.gpu_num = torch.cuda.device_count()
        self.mps_enabled = getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available()
        logging.getLogger(LOGGER_NAME).info(f"GPU num: {self.gpu_num}, mps_enabled: {self.mps_enabled}, directml_available: {directml_available}")

    def get_pytorch_device(self, id: int) -> torch.device:
        res = self._get_pytorch_device(id)
        logging.getLogger(LOGGER_NAME).info(f"get_pytorch_device: {res}")
        return res

    def _get_pytorch_device(self, id: int) -> torch.device:

        if id < 0 or self.gpu_num == 0:
            if self.mps_enabled is False:
                dev = torch.device("cpu")
            else:
                dev = torch.device("mps")
        else:
            if id < self.gpu_num:
                if directml_available:
                    dev = torch_directml.device(device_id=id)
                    dev = torch.device(dev)
                else:
                    dev = torch.device("cuda", index=id)
            else:
                print("[Voice Changer] pytorch failed to detect device. fallback to cpu")
                dev = torch.device("cpu")
        return dev

    def get_onnx_execution_provider(self, device_id: int) -> tuple[list[str], list[dict]]:  # プロバイダのリストと、対応するオプションのリスト
        res = self._get_onnx_execution_provider(device_id)
        logging.getLogger(LOGGER_NAME).info(f"get_onnx_execution_privider: {res}")
        return res

    def _get_onnx_execution_provider(self, device_id: int) -> tuple[list[str], list[dict]]:  # プロバイダのリストと、対応するオプションのリスト
        available_providers = onnxruntime.get_available_providers()
        logging.getLogger(LOGGER_NAME).info(f"available_providers: {available_providers}")
        cuda_info = GPUDeviceManager.get_instance().get_cuda_info()
        gpu_info = GPUDeviceManager.get_instance().get_gpu_info()
        cuda_len = len(cuda_info)
        gpu_len = len(gpu_info) - 1  # gpu_infoにはcpuが含まれている
        gpu_num = max(cuda_len, gpu_len)
        # dev_num = torch.cuda.device_count()
        logging.getLogger(LOGGER_NAME).info(f"gpu_num: {gpu_num}, cuda_len: {cuda_len}, gpu_len: {gpu_len}")
        if device_id >= 0 and "CUDAExecutionProvider" in available_providers and gpu_num > 0:
            if device_id < gpu_num:  # ひとつ前のif文で弾いてもよいが、エラーの解像度を上げるため一段下げ。
                return ["CUDAExecutionProvider"], [{"device_id": device_id}]
            else:
                logging.getLogger(LOGGER_NAME).info(f"device detection error, fallback to cpu. device_id: {device_id} >= dev_num: {gpu_num}")
                return ["CPUExecutionProvider"], [
                    {
                        "intra_op_num_threads": 8,
                        "execution_mode": onnxruntime.ExecutionMode.ORT_PARALLEL,
                        "inter_op_num_threads": 8,
                    }
                ]
        elif device_id >= 0 and "DmlExecutionProvider" in available_providers:
            return ["DmlExecutionProvider"], [{"device_id": device_id}]
        else:
            return ["CPUExecutionProvider"], [
                {
                    "intra_op_num_threads": 8,
                    "execution_mode": onnxruntime.ExecutionMode.ORT_PARALLEL,
                    "inter_op_num_threads": 8,
                }
            ]

    def set_force_tensor(self, force_tensor: bool):
        self.forceTensor = force_tensor

    def half_precision_available(self, id: int) -> bool:
        if self.gpu_num == 0:
            return False
        if id < 0:
            return False
        # if self.forceTensor:
        #     return False

        try:
            gpu_name = torch.cuda.get_device_name(id).upper()
            if ("16" in gpu_name and "V100" not in gpu_name) or "P40" in gpu_name.upper() or "1070" in gpu_name or "1080" in gpu_name:
                return False
        except Exception as e:
            print(e)
            return False

        cap = torch.cuda.get_device_capability(id)
        if cap[0] < 7:  # コンピューティング機能が7以上の場合half precisionが使えるとされている（が例外がある？T500とか）
            return False

        return True

    def get_device_memory(self, id: int) -> int:
        try:
            return torch.cuda.get_device_properties(id).total_memory
        except Exception as e:
            print(e)
            return 0
