export class FileUploaderClient {
    #baseUrl: string;
    enableFlatPath: boolean = false;
    constructor() {
        this.#baseUrl = "";
    }

    setBaseUrl = (baseUrl: string): void => {
        if (baseUrl.endsWith("/")) {
            baseUrl = baseUrl.slice(0, -1);
        }
        this.#baseUrl = baseUrl;
    };
    setEnableFlatPath = (enable: boolean): void => {
        this.enableFlatPath = enable;
    };
    generatePath = (path: string): string => {
        if (this.enableFlatPath) {
            return path[0] + path.slice(1).replace(/\//g, "_");
        }
        return path;
    };

    uploadFile = async (dir: string, file: File, onprogress: (progress: number, end: boolean) => void) => {
        const path = this.#baseUrl + this.generatePath("/api/uploader/upload_file_chunk");
        onprogress(0, false);
        const size = 1024 * 1024;
        let index = 0; // index値
        const fileLength = file.size;
        const filename = dir + file.name;
        const fileChunkNum = Math.ceil(fileLength / size);

        while (true) {
            const promises: Promise<void>[] = [];
            for (let i = 0; i < 10; i++) {
                if (index * size >= fileLength) {
                    break;
                }
                const chunk = file.slice(index * size, (index + 1) * size);

                const p = new Promise<void>((resolve) => {
                    const formData = new FormData();
                    formData.append("file", new Blob([chunk]));
                    formData.append("filename", `${filename}`);
                    formData.append("index", `${index}`);
                    const request = new Request(path, {
                        method: "POST",
                        body: formData,
                    });
                    fetch(request).then(async (_response) => {
                        console.log(await _response.text());
                        resolve();
                    });
                });
                index += 1;
                promises.push(p);
            }

            await Promise.all(promises);
            if (index * size >= fileLength) {
                break;
            }
            onprogress(Math.floor((index / (fileChunkNum + 1)) * 100), false);
        }
        return fileChunkNum;
    };

    concatUploadedFile = async (filename: string, chunkNum: number) => {
        const path = this.#baseUrl + this.generatePath("/api/uploader/concat_uploaded_file_chunk");
        await new Promise<void>((resolve) => {
            const formData = new FormData();
            formData.append("filename", filename);
            formData.append("filename_chunk_num", "" + chunkNum);
            const request = new Request(path, {
                method: "POST",
                body: formData,
            });
            fetch(request).then(async (response) => {
                console.log(await response.text());
                resolve();
            });
        });
    };
}
