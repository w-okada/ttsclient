import { style } from "@vanilla-extract/css";
import { globaVars } from "./001_global.css";

export const modelSlotArea = style({
    display: "inline-block",
    background: globaVars.color.companyColor2,
    borderRadius: "10px",
    padding: "5px 20px 20px 20px",
});
export const modelSlotArea2 = style({
    display: "inline-block",
    background: globaVars.color.companyColor1,
    borderRadius: "10px",
    padding: "5px 20px 20px 20px",
});

export const modelSlotPane = style({
    display: "flex",
    flexDirection: "row",
    gap: "5px",
});

export const modelSlotTitle = style({
    fontSize: "0.8rem",
    fontWeight: 700,
    color: "#dee",
    // textShadow: "3px 1px 1px #999",
});

export const modelSlotTilesContainer = style({
    display: "flex",
    flexDirection: "row",
    gap: "2px",
    flexWrap: "wrap",
    overflowY: "scroll",
    maxHeight: "12rem",
    "::-webkit-scrollbar": {
        width: "10px",
        height: "10px",
    },
    "::-webkit-scrollbar-track": {
        backgroundColor: "#eee",
        borderRadius: "3px",
    },
    "::-webkit-scrollbar-thumb": {
        background: "#f7cfec80",
        borderRadius: "3px",
    },
});
export const buttons = style({
    display: "flex",
    gap: "10px",
    flexDirection: "column",
    width: "4rem",
});

export const buttonGroup = style({
    // height: "40%",
});
export const button = style({
    border: "solid 2px #999",
    color: "white",
    fontSize: "0.8rem",
    borderRadius: "2px",
    background: "#333",
    cursor: "pointer",
    padding: "2px",
    textAlign: "center",
    width: "3rem",
    ":hover": {
        border: "solid 2px #faa",
    },
});
export const buttonActive = style({
    border: "solid 2px #faa",
    background: "#343",
});

export const modelSlotTileContainer = style({
    width: "6rem",
    height: "6rem",
    borderRadius: "2px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    ":hover": {
        background: "#43030c",
    },
});
export const modelSlotTileContainerSelected = style({
    background: "#43030c",
});

export const modelSlotTileIconDiv = style({
    width: "5rem",
    height: "5rem",
    paddingTop: "4px",
    position: "relative",
});
export const modelSlotTileIcon = style({
    width: "5rem",
    height: "5rem",
    objectFit: "contain",
});
export const modelSlotTileIconNoEntry = style({
    color: "#e1d3dd",
    position: "absolute",
    top: "2rem",
});
export const modelSlotTileDscription = style({
    fontSize: "0.7rem",
    fontWeight: "700",
    color: "navajowhite",
    paddingTop: "4px",
});

export const modelSlotTileVctype = style({
    position: "absolute",
    fontSize: "0.6rem",
    fontWeight: "800",
    top: "5px",
    left: "2px",
    background: "RGBA(10, 200, 100, 0.6)",
    borderRadius: "5px",
    padding: "0px 2px 0px 2px",
});
