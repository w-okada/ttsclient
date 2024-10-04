import { useMemo } from "react";
import { characterArea } from "../../styles/characterArea.css";
import React from "react";
import { CharacterAreaPortrait } from "./003-1_CharacterAreaPortrait";
import { CharacterAreaControl } from "./003-2_CharacterAreaControl";

export const CharacterArea = () => {
    const area = useMemo(() => {
        return (
            <div className={characterArea}>
                <CharacterAreaPortrait></CharacterAreaPortrait>
                <CharacterAreaControl></CharacterAreaControl>
            </div>
        );
    }, []);
    return area;
};
