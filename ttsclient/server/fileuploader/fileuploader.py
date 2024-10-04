from pathlib import Path
import shutil
from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from ttsclient.server.validation_error_logging_route import ValidationErrorLoggingRoute


class UploadableFile(BaseModel):
    title: str
    filename: str


class FileuploaderInfo(BaseModel):
    uploadable_files: list[UploadableFile] = []


class FileuploaderUploadfileChunkResult(BaseModel):
    uploaded_filename: str


class FileuploaderConcatUploadedFileChunkResult(BaseModel):
    generated_filename: str


class EasyFileUploader:
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(exist_ok=True)
        self.info = FileuploaderInfo(
            uploadable_files=[
                UploadableFile(title="model file", filename="model_file"),
                UploadableFile(title="index file", filename="index_file"),
            ],
        )

        self.router = APIRouter()
        self.router.route_class = ValidationErrorLoggingRoute
        self.router.add_api_route("/api/uploader/info", self.get_info, methods=["GET"])
        self.router.add_api_route("/api/uploader/upload_file_chunk", self.post_upload_file_chunk, methods=["POST"])
        self.router.add_api_route("/api/uploader/concat_uploaded_file_chunk", self.post_concat_uploaded_file_chunk, methods=["POST"])

        self.router.add_api_route("/api_uploader_info", self.get_info, methods=["GET"])
        self.router.add_api_route("/api_uploader_upload_file_chunk", self.post_upload_file_chunk, methods=["POST"])
        self.router.add_api_route("/api_uploader_concat_uploaded_file_chunk", self.post_concat_uploaded_file_chunk, methods=["POST"])

    def get_info(self):
        return self.info

    # def _sanitize_filename(self, filename: str) -> bool:
    # upploadable_filenames = [file.filename for file in self.info.uploadable_files]
    # if filename not in upploadable_filenames:
    #     raise RuntimeError(f"filename {filename} is not allowed. Allowed filenames are {upploadable_filenames}")
    # return True
    def _sanitize_filename(self, filename: str) -> str:
        path = Path(filename)
        filename = path.name[:100]
        return filename

    #######################################
    # Upload File Chunk
    # TEST:
    #  curl -X POST -F "filename=data1" -F "index=0" -F "file=@test_data/data0.txt" http://localhost:8001/api/uploader/upload_file_chunk
    #  curl -X POST -F "filename=data1" -F "index=1" -F "file=@test_data/data0.txt" http://localhost:8001/api/uploader/upload_file_chunk
    #  curl -X POST -F "filename=data1" -F "index=2" -F "file=@test_data/data2.txt" http://localhost:8001/api/uploader/upload_file_chunk
    #######################################
    def post_upload_file_chunk(
        self,
        file: UploadFile = File(...),
        filename: str = Form(...),
        index: int = Form(...),
    ):
        target_path = self._upload_file(self.upload_dir, file, filename, index)
        return FileuploaderUploadfileChunkResult(uploaded_filename=str(target_path))

    def _upload_file(self, upload_path: Path, file: UploadFile, filename: str, index: int):
        filename = self._sanitize_filename(filename)
        indexed_filename = f"{filename}_{index}"
        fileobj = file.file
        target_path = upload_path / indexed_filename
        target_file = open(target_path, "wb+")
        shutil.copyfileobj(fileobj, target_file)
        target_file.close()
        return target_path

    #######################################
    # Concat File
    # TEST:
    #  curl -X POST -F "filename=data1"  -F "filenameChunkNum=3" http://localhost:8001/concat_uploaded_file_chunk
    #######################################
    def post_concat_uploaded_file_chunk(self, filename: str = Form(...), filename_chunk_num: int = Form(...)):
        filepath = self._concat_file_chunks(self.upload_dir, filename, filename_chunk_num)
        return FileuploaderConcatUploadedFileChunkResult(generated_filename=str(filepath))

    def _concat_file_chunks(self, upload_path: Path, filename: str, filename_chunk_num: int):
        filename = self._sanitize_filename(filename)
        filepath = upload_path / filename

        if filepath.exists():
            filepath.unlink()

        with open(filepath, "ab") as out:
            for i in range(filename_chunk_num):
                chunk_path = Path(f"{filepath}_{i}")
                chunk_file = open(chunk_path, "rb")
                out.write(chunk_file.read())
                chunk_file.close()
                chunk_path.unlink()
            out.close()
        return filepath
