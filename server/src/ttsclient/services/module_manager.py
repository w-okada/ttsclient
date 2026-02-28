from ttsclient.models.module import ModuleStatus


class ModuleManager:
    _instance: "ModuleManager | None" = None

    def __init__(self) -> None:
        self._modules: list[ModuleStatus] = []

    @classmethod
    def get_instance(cls) -> "ModuleManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload(self) -> list[ModuleStatus]:
        # TODO: モジュール状態の検出
        self._modules = []
        return self._modules

    def get_modules(self) -> list[ModuleStatus]:
        return self._modules
