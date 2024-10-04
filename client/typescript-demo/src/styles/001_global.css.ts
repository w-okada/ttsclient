import { createGlobalTheme, createTheme, createThemeContract, globalStyle, style } from "@vanilla-extract/css";

export const globaVars = createGlobalTheme(":root", {
    color: {
        companyColor1: "rgba(64, 119, 187, 1)",
        companyColor2: "rgba(29, 47, 78, 1)",
        textLightMode: "rgba(0, 0, 0, 1)",
        textDarkMode: "rgba(255, 255, 255, 1)",
        backgroundLightMode: "rgba(255, 255, 255, 1)",
        backgroundDarkMode: "rgba(5, 5, 10, 1)",

        titleLightMode: "rgba(70, 70, 70, 1)",
        titleDarkMode: "rgba(200, 200, 200, 1)",

        dialogBackgroundColor: "rgba(255, 255, 255, 1)",
        dialogBorderColor: "rgba(100, 100, 100, 1)",
        dialogShadowColor: "rgba(0, 0, 0, 0.3)",
    },
});

export const themeContract = createThemeContract({
    color: {
        text: null,
        background: null,
        title: null,
    },
});

export const lightTheme = createTheme(themeContract, {
    color: {
        background: globaVars.color.backgroundLightMode,
        text: globaVars.color.textLightMode,
        title: globaVars.color.titleLightMode,
    },
});
export const darkTheme = createTheme(themeContract, {
    color: {
        background: globaVars.color.backgroundDarkMode,
        text: globaVars.color.textDarkMode,
        title: globaVars.color.titleDarkMode,
    },
});


globalStyle("*", {
    margin: 0,
    padding: 0,
    boxSizing: "border-box",
    fontFamily: '"Poppins", sans-serif',
});

globalStyle("html", {
    fontSize: "16px",
});

globalStyle("body", {
    height: "100%",
    width: "100%",
    overflowY: "scroll",
    overflowX: "hidden",
    color: themeContract.color.text,
    background: `linear-gradient(45deg, ${globaVars.color.companyColor1} 0, 1%, ${globaVars.color.companyColor2} 1% 5%, ${themeContract.color.background} 5% 90%, ${globaVars.color.companyColor1} 90% 95%, ${globaVars.color.companyColor2} 95% 100%)`,
    padding: "0rem 2rem 2rem 2rem",
    userSelect: "none",
});
