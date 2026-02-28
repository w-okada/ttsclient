from fastapi import APIRouter

from ttsclient.models.tts_configuration import TTSConfiguration
from ttsclient.services.configuration_manager import ConfigurationManager

router = APIRouter(prefix="/api/configuration-manager")


@router.get("/configuration", response_model=TTSConfiguration)
async def get_configuration(reload: bool = False):
    manager = ConfigurationManager.get_instance()
    if reload:
        manager.reload()
    return manager.get_tts_configuration()


@router.put("/configuration", response_model=TTSConfiguration)
async def put_configuration(configuration: TTSConfiguration):
    manager = ConfigurationManager.get_instance()
    manager.set_tts_configuration(configuration)
    return manager.get_tts_configuration()
