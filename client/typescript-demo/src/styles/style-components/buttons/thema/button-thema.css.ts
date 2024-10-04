import { createTheme, createThemeContract } from "@vanilla-extract/css";

export const buttonThemeContract = createThemeContract({
    color: {
        text: null,
        background: null,
        border: null,

        textHover: null,
        backgroundHover: null,
        borderHover: null,

        textActive: null,
        backgroundActive: null,
        borderActive: null,

        textDisabled: null,
        backgroundDisabled: null,
        borderDisabled: null,
    },
    border: {
        radius: null,
        width: null
    }
});

export const headerButtonThema = createTheme(buttonThemeContract, {
    color: {
        text: "#000000",
        background: "#ffffff",
        border: "#000000",
        textHover: "#000000",
        backgroundHover: "#e0e0e0",
        borderHover: "#000000",

        textActive: "#000000",
        backgroundActive: "#00ff00",
        borderActive: "#000000",

        textDisabled: "#000000",
        backgroundDisabled: "#efefef",
        borderDisabled: "#000000",
    },
    border: {
        radius: "15px",
        width: "1px"
    }
});


export const normalButtonThema = createTheme(buttonThemeContract, {
    color: {
        text: "#000000",
        background: "#ffffff",
        border: "#000000",
        textHover: "#000000",
        backgroundHover: "#e0e0e0",
        borderHover: "#000000",

        textActive: "#000000",
        backgroundActive: "#00ff00",
        borderActive: "#000000",

        textDisabled: "#000000",
        backgroundDisabled: "#efefef",
        borderDisabled: "#000000",
    },
    border: {
        radius: "5px",
        width: "1px"
    }
});


export const modelSlotButtonThema = createTheme(buttonThemeContract, {
    color: {
        text: "#ffffff",
        background: "#333333",
        border: "#999999",
        textHover: "#ffffff",
        backgroundHover: "333333",
        borderHover: "#ffaaaa",

        textActive: "#ffffff",
        backgroundActive: "#334433",
        borderActive: "#ffaaaa",
        textDisabled: "#000000",
        backgroundDisabled: "#efefef",
        borderDisabled: "#000000",
    },
    border: {
        radius: "5px",
        width: "2px"

    }
});