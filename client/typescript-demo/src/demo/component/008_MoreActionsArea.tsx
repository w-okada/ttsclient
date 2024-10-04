import { useMemo } from "react";
import React from "react";
import { configSubAreaLong } from "../../styles/configArea.css";
import { MoreActionsButtons } from "./008-x-1_moreButtons";

export const MoreActionsArea = () => {
    const area = useMemo(() => {
        return (
            <div className={configSubAreaLong}>
                <MoreActionsButtons></MoreActionsButtons>
            </div>
        );
    }, []);
    return area;
};
