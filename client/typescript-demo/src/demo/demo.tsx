import React, { useEffect } from "react";
import { GuiStateProvider } from "./GuiStateProvider";
import { Dialogs } from "./component/dialogs/Dialogs";
import { Dialogs2 } from "./component/dialogs/Dialogs2";
import { HeaderArea } from "./component/001_HeaderArea";
import { ModelSlotArea } from "./component/002-1_ModelSlotArea";
import { CharacterArea } from "./component/003_CharacterArea";
import { configArea, configAreaRow } from "../styles/configArea.css";
import { MoreActionsArea } from "./component/008_MoreActionsArea";
import { useAppState } from "../002_AppStateProvider";
import { VoiceCharacterSlotArea } from "./component/002-2_VoiceCharacterSlotArea";
import { darkTheme, lightTheme, spacer_h10px } from "../styles";
import { TextInputArea } from "./component/004_TextInputArea";
import { DeviceSettingArea } from "./component/005_DeviceSettingArea";

export const Demo = () => {
    const { displayColorMode } = useAppState();
    useEffect(() => {
        const bodyClass = displayColorMode == "light" ? lightTheme : darkTheme;
        document.body.className = bodyClass
    }, [displayColorMode])
    return (
        <GuiStateProvider>
            <Dialogs2 />
            <Dialogs />
            <HeaderArea></HeaderArea>
            <ModelSlotArea></ModelSlotArea>
            <div className={spacer_h10px}></div>
            <VoiceCharacterSlotArea ></VoiceCharacterSlotArea >
            <CharacterArea></CharacterArea>
            <TextInputArea></TextInputArea>
            <DeviceSettingArea></DeviceSettingArea>

            <div className={configArea}>
                <div className={configAreaRow}>
                    <MoreActionsArea></MoreActionsArea>
                </div>
            </div>
            <div className={configArea}>
            </div>
        </GuiStateProvider>
    );
};
