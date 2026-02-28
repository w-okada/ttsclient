from fastapi import APIRouter

from ttsclient.const import UPLOAD_DIR
from ttsclient.models.sample import SampleDownloadParam
from ttsclient.services.sample_manager import SampleManager

router = APIRouter(prefix="/api/sample-manager")


@router.get("/samples")
async def get_samples(reload: bool = False):
    manager = SampleManager.get_instance()
    if reload:
        manager.reload()
    return manager.get_samples()


@router.post("/samples/operation/download")
async def download_sample(param: SampleDownloadParam):
    manager = SampleManager.get_instance()
    manager.download(UPLOAD_DIR, param)
    return {"message": "ok"}
