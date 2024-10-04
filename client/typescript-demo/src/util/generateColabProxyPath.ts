


export const getGenerateGetPathFunc = (serverBaseUrl: string, colabProxy: boolean) => {
    const generateColabGetProxyPath = (path: string): string => {
        return serverBaseUrl + "/get_proxy?path=" + path;
    }

    const generateNormalPath = (path: string): string => {
        return serverBaseUrl + path
    }
    return colabProxy ? generateColabGetProxyPath : generateNormalPath
}