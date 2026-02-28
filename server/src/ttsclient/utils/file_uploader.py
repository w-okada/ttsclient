import shutil
from pathlib import Path

from fastapi import File, Form, UploadFile
from pydantic import BaseModel


class UploadableFile(BaseModel):
    title: str
    filename: str


class FileuploaderInfo(BaseModel):
    uploadable_files: list[UploadableFile] = []


class FileuploaderUploadFileChunkResult(BaseModel):
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

    def get_info(self) -> FileuploaderInfo:
        return self.info

    def _sanitize_filename(self, filename: str) -> str:
        path = Path(filename)
        return path.name[:100]

    def upload_file_chunk(
        self,
        file: UploadFile = File(...),
        filename: str = Form(...),
        index: int = Form(...),
    ) -> FileuploaderUploadFileChunkResult:
        filename = self._sanitize_filename(filename)
        indexed_filename = f"{filename}_{index}"
        target_path = self.upload_dir / indexed_filename
        with open(target_path, "wb+") as target_file:
            shutil.copyfileobj(file.file, target_file)
        return FileuploaderUploadFileChunkResult(uploaded_filename=str(target_path))

    def concat_uploaded_file_chunk(
        self,
        filename: str = Form(...),
        filename_chunk_num: int = Form(...),
    ) -> FileuploaderConcatUploadedFileChunkResult:
        filename = self._sanitize_filename(filename)
        filepath = self.upload_dir / filename

        if filepath.exists():
            filepath.unlink()

        with open(filepath, "ab") as out:
            for i in range(filename_chunk_num):
                chunk_path = self.upload_dir / f"{filename}_{i}"
                with open(chunk_path, "rb") as chunk_file:
                    out.write(chunk_file.read())
                chunk_path.unlink()

        return FileuploaderConcatUploadedFileChunkResult(generated_filename=str(filepath))
