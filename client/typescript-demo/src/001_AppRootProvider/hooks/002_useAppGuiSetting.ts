import { useEffect, useState } from "react";

export type AppGuiSetting = {
    type: "demo";
    lang: string[];
    inputChunkSec: number[];
    extraFrameSec: number[];
};

export type AppGuiSettingState = {
    guiSettingLoaded: boolean;
    setting: AppGuiSetting | null;
    version: string | null;
    edition: string | null;
    reloadEditionDummy: () => Promise<void>
};

export type AppGuiSettingStateAndMethod = AppGuiSettingState & {};

export type UseAppGuiSettingProps = {
    generateGetPathFunc: (path: string) => string
};

// バージョン等の管理。HTTPで取得する情報。
export const useAppGuiSetting = (props: UseAppGuiSettingProps): AppGuiSettingStateAndMethod => {
    const [guiSettingLoaded, setGuiSettingLoaded] = useState<boolean>(false);
    const [setting, setSetting] = useState<AppGuiSetting | null>(null);
    const [version, setVersion] = useState<string | null>(null);
    const [edition, setEdition] = useState<string | null>(null);

    useEffect(() => {
        const url = props.generateGetPathFunc("/assets/gui_settings/GUI.json");
        const getVersionInfo = async () => {

            console.log(`getVersionInfo: ${url}`);
            const res = await fetch(url, {
                method: "GET",
            });
            const setting = (await res.json()) as AppGuiSetting;
            setSetting(setting);
        };
        getVersionInfo();
    }, [props.generateGetPathFunc]);

    useEffect(() => {
        const url = props.generateGetPathFunc("/assets/gui_settings/version.txt");

        const getVersionInfo = async () => {
            const res = await fetch(url, {
                method: "GET",
            });
            const version = await res.text();
            setVersion(version);
        };
        getVersionInfo();
    }, [props.generateGetPathFunc]);

    useEffect(() => {
        const url = props.generateGetPathFunc("/assets/gui_settings/edition.txt");
        const getVersionInfo = async () => {
            const res = await fetch(url, {
                method: "GET",
            });
            const edition = await res.text();
            setEdition(edition);
        };
        getVersionInfo();
    }, [props.generateGetPathFunc]);

    useEffect(() => {
        if (version !== null && edition !== null) {
            setGuiSettingLoaded(true);
        }
    }, [version, edition]);

    const reloadEditionDummy = async () => {
        const url = props.generateGetPathFunc("/assets/gui_settings/edition.txt");
        const res = await fetch(url, {
            method: "GET",
        });
        const edition = await res.text();
        console.log("edition", edition)
        // setEdition(edition);
    }

    return {
        guiSettingLoaded,
        setting,
        version,
        edition,
        reloadEditionDummy,
    };
};
