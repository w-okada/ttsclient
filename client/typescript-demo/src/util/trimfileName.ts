export const trimfileName = (name: string, length: number) => {
    const trimmedName = name.replace(/^.*[\\\/]/, "");
    if (trimmedName.length > length) {
        return trimmedName.substring(0, length) + "...";
    } else {
        return trimmedName;
    }
};
