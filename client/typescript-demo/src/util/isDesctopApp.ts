export const isDesktopApp = () => {
    if (navigator.userAgent.indexOf("Electron") >= 0) {
        return true;
    } else {
        return false;
    }
};
