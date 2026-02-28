from fastapi import APIRouter, File, Form, UploadFile

from ttsclient.const import UPLOAD_DIR
from ttsclient.utils.file_uploader import (
    EasyFileUploader,
    FileuploaderConcatUploadedFileChunkResult,
    FileuploaderInfo,
    FileuploaderUploadFileChunkResult,
)

router = APIRouter()
_uploader = EasyFileUploader(UPLOAD_DIR)


@router.get("/api/uploader/info", response_model=FileuploaderInfo)
async def get_info():
    return _uploader.get_info()


@router.post("/api/uploader/upload_file_chunk", response_model=FileuploaderUploadFileChunkResult)
async def upload_file_chunk(
    file: UploadFile = File(...),
    filename: str = Form(...),
    index: int = Form(...),
):
    return _uploader.upload_file_chunk(file=file, filename=filename, index=index)


@router.post("/api/uploader/concat_uploaded_file_chunk", response_model=FileuploaderConcatUploadedFileChunkResult)
async def concat_uploaded_file_chunk(
    filename: str = Form(...),
    filename_chunk_num: int = Form(...),
):
    return _uploader.concat_uploaded_file_chunk(filename=filename, filename_chunk_num=filename_chunk_num)
