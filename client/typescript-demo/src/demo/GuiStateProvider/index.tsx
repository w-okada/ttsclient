import React, { useContext, useEffect, useState } from "react";
import { ReactNode } from "react";
import { useAppState } from "../../002_AppStateProvider";
import { useAppRoot } from "../../001_AppRootProvider";

export const DialogName = {
    none: "none",
    startingNoticeDialog: "startingNoticeDialog",
    modelSlotManagerMainDialog: "modelSlotManagerMainDialog",
    modelSlotManagerFileUploaderDialog: "modelSlotManagerFileUploaderDialog",
    modelSlotManagerSamplesDialog: "modelSlotManagerSamplesDialog",
    modelSlotManagerEditorDialog: "modelSlotManagerEditorDialog",
    voiceCharacterManagerMainDialog: "voiceCharacterManagerMainDialog",
    voiceCharacterManagerFileUploaderDialog: "voiceCharacterManagerFileUploaderDialog",
    advancedSettingDialog: "advancedSettingDialog",
    exportToOnnxDialog: "exportToOnnxDialog",
    mergeLabDialog: "mergeLabDialog",
    aboutModelDialog: "aboutModelDialog",
    aboutVoiceDialog: "aboutVoiceDialog",
} as const;
export type DialogName = (typeof DialogName)[keyof typeof DialogName];

export const DialogName2 = {
    none: "none",
    textInputDialog: "textInputDialog",
    confirmDialog: "confirmDialog",
    waitDialog: "waitDialog",
    selectInputDialog: "selectInputDialog",
} as const;
export type DialogName2 = (typeof DialogName2)[keyof typeof DialogName2];

type Props = {
    children: ReactNode;
};

type GuiStateAndMethod = {
    dialogName: DialogName;
    setDialogName: (val: DialogName) => void;
    dialog2Name: DialogName2;
    setDialog2Name: (val: DialogName2) => void;
    dialog2Props: Dialog2Props<any> | null;
    setDialog2Props: (val: Dialog2Props<any> | null) => void;
};

const GuiStateContext = React.createContext<GuiStateAndMethod | null>(null);
export const useGuiState = (): GuiStateAndMethod => {
    const state = useContext(GuiStateContext);
    if (!state) {
        throw new Error("useGuiState must be used within GuiStateProvider");
    }
    return state;
};

type Dialog2Props<T> = {
    title: string;
    instruction: string;
    resolve: (value: T | PromiseLike<T>) => void;
    defaultValue: T;
    options: { label: string; value: T }[] | null;
};

export const GuiStateProvider = ({ children }: Props) => {
    const [dialogName, setDialogName] = useState<DialogName>(DialogName.none);
    const [dialog2Name, setDialog2Name] = useState<DialogName2>(DialogName2.none);
    const [dialog2Props, setDialog2Props] = useState<Dialog2Props<any> | null>(null);
    const { } = useAppRoot();

    useEffect(() => {
        const url = new URL(location.href);
        const first = url.searchParams.get("first");
        if (first !== "false") {
            setDialogName("startingNoticeDialog");
        }
    }, []);

    const providerValue: GuiStateAndMethod = {
        dialogName,
        setDialogName,
        dialog2Name,
        setDialog2Name,
        dialog2Props,
        setDialog2Props,
    };

    return <GuiStateContext.Provider value={providerValue}>{children}</GuiStateContext.Provider>;
};
