import { style } from "@vanilla-extract/css";
import { themeContract } from "./001_global.css";

export const headerArea = style({
    display: "flex",
    flexDirection: "column",
    width: "100%",
});

export const titleArea = style({
    display: "flex",
    flexDirection: "row",
    gap: "5px",
    alignItems: "flex-end",
});

export const title = style({
    fontSize: "1.8rem",
    fontWeight: 700,
    color: themeContract.color.title,
    textShadow: "0 0 2px #333",
});

export const titleVersion = style({
    fontSize: "0.9rem",
    ":hover": {
        color: "red",
    },
});

export const iconArea = style({
    display: "flex",
    flexDirection: "row",
    gap: "20px",
});

export const iconGroup = style({
    display: "flex",
    flexDirection: "row",
    gap: "10px",
});

export const tooltip = style({
    // width: "100%",
    position: "relative",
    cursor: "pointer",
    display: "inline-block",
    zIndex: "10",
});
export const tooltipText = style({
    display: "none",
    position: "absolute",
    padding: "4px",
    fontSize: "1rem",
    fontWeight: 700,
    lineHeight: "2rem",
    color: "#fff",
    borderRadius: "5px",
    background: "#444",
    whiteSpace: "nowrap",
    zIndex: "100",
    ":before": {
        content: "",
        position: "absolute",
        top: "-1.4rem",
        border: "12px solid transparent",
        borderTop: "16px solid #444",
        marginLeft: "0rem",
        transform: "rotateZ(180deg)",
    },
    selectors: {
        [`${tooltip}:hover &`]: {
            display: "inline-block",
            top: "30px",
            left: "0px",
        },
    },
});
export const tooltipText100px = style({
    // width: "100px",
});
export const tooltipTextThin = style({
    lineHeight: "1rem",
});
export const tooltipTextLower = style({
    selectors: {
        [`${tooltip}:hover &`]: {
            display: "inline-block",
            top: "60px",
            left: "0px",
        },
    },
});

export const button = style({
    border: "solid 2px #999",
    color: "white",
    fontSize: "0.8rem",
    borderRadius: "5px",
    background: "#666",
    cursor: "pointer",
    padding: "2px",
    top: "-2px",

    ":hover": {
        backgroundColor: "#aa8",
    },
});
