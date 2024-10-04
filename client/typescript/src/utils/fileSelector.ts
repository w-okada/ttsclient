export const fileSelector = async (regex: string) => {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    const p = new Promise<File>((resolve, reject) => {
        fileInput.onchange = (e) => {
            if (e.target instanceof HTMLInputElement == false) {
                console.log("invalid target!", e.target);
                reject("invalid target");
                return null;
            }
            const target = e.target as HTMLInputElement;
            if (!target.files || target.files.length == 0) {
                reject("no file selected");
                return null;
            }

            if (regex != "" && target.files[0].type.match(regex)) {
                reject(`not target file type ${target.files[0].type}`);
                return null;
            }
            resolve(target.files[0]);
            return null;
        };
        fileInput.oncancel = () => {
            reject("cancel");
        };
        fileInput.click();
    });
    return await p;
};

export const fileSelectorAsDataURL = async (regex: string) => {
    const f = await fileSelector(regex);
    if (!f) {
        return f;
    }

    const url = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onload = () => {
            console.log("load data", reader.result as string);
            resolve(reader.result as string);
        };
        reader.readAsDataURL(f);
    });
    return url;
};
