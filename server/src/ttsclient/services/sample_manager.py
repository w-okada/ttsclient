from pathlib import Path

from ttsclient.models.sample import SampleDownloadParam, SampleInfoMember


class SampleManager:
    _instance: "SampleManager | None" = None

    def __init__(self) -> None:
        self._samples: list[SampleInfoMember] = []

    @classmethod
    def get_instance(cls) -> "SampleManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload(self) -> list[SampleInfoMember]:
        # TODO: サンプル一覧の取得
        self._samples = []
        return self._samples

    def get_samples(self) -> list[SampleInfoMember]:
        return self._samples

    def download(self, upload_dir: Path, param: SampleDownloadParam) -> None:
        # TODO: サンプルダウンロード処理
        pass
