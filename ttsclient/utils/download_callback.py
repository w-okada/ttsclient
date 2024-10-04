from typing import Callable
from ttsclient.tts.data_types.module_manager_data_types import ModuleDownloadStatus
from ttsclient.utils.is_running_on_colab import is_running_on_colab

if is_running_on_colab():
    # print("load tqdm for notebook")
    from tqdm.notebook import tqdm
else:
    # print("load normal notebook")
    from tqdm import tqdm  # type: ignore


def get_download_callback() -> Callable:
    pbar_dict_module: dict[str, tqdm] = {}

    def download_callback(status: list[ModuleDownloadStatus]):
        position = 0
        for s in status:
            if s.id not in pbar_dict_module:
                pbar_dict_module[s.id] = tqdm(
                    total=100,
                    unit="%",
                    desc=f"Downloading {s.id[:10]}",
                    leave=False,
                    position=position,
                )
                position += 1
            pbar = pbar_dict_module[s.id]
            pbar.n = int(s.progress * 100)
            pbar.refresh()
            if s.status == "done":
                pbar.close()

    return download_callback
