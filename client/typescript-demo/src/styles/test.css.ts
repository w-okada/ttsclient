import { style } from "@vanilla-extract/css";

export const testRowContainer = style({
    display: "flex",
    flexDirection: "column",
    width: "100%",
    height: "100%",
    margin: "10px 10px 10px 10px",
    overflowY: "scroll",
    overflowX: "hidden",
});

export const split_4_2_4 = style({
    display: "flex",
    width: "100%",
    margin: "10px 10px 10px 10px",

    selectors: {
        "&:hover:not(:active)": {
            color: "red",
        },
    },
});

export const rowTitle = style({
    selectors: {
        [`${split_4_2_4} &`]: {
            width: "40%",
        },
    },
});

export const rowButton = style({
    selectors: {
        [`${split_4_2_4} &`]: {
            width: "20%",
        },
    },
});

export const rowDesc = style({
    selectors: {
        [`${split_4_2_4} &`]: {
            width: "40%",
        },
    },
});
