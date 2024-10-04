import os
import requests
import zipfile

# URLとダウンロード先のファイルパスを定義
url = "https://huggingface.co/wok000/python_modules/resolve/main/eunjeon-0.4.0-cp312-cp312-win_amd64.zip"
download_path = "eunjeon-0.4.0-cp312-cp312-win_amd64.zip"
extract_to = "ext_lib"


def download_modules():
    # ダウンロード関数
    def download_file(url, local_filename):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename

    # ファイルをダウンロード
    print(f"Downloading {url} to {download_path}...")
    download_file(url, download_path)
    print("Download complete.")

    # 解凍ディレクトリが存在しない場合は作成
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # ZIPファイルを解凍
    print(f"Extracting {download_path} to {extract_to}...")
    with zipfile.ZipFile(download_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")
