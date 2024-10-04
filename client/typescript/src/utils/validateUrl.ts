export const validateUrl = (url: string) => {
    if (url?.endsWith("/")) {
        return url.substring(0, url.length - 1);
    }
    return url;
};
