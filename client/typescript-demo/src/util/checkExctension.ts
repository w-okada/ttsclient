export const checkExtention = (filename: string, acceptExtentions: string[]) => {
    const ext = filename.split(".").pop();
    if (!ext) {
        return false;
    }
    return acceptExtentions.includes(ext);
};
