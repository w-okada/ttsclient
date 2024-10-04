import { style } from "@vanilla-extract/css";

export const textInputArea = style({
    display: "flex",
    flexDirection: "column",
    gap: "15px",
    padding: "20px",
    borderTop: "solid 1px #999",
});
export const portraitArea = style({
    width: "20rem",
    height: "20rem",
});
export const portraitContainer = style({
    position: "relative",
    width: "20rem",
    height: "20rem",
    borderRadius: "1rem",
    overflow: "hidden",
});
export const portrait = style({
    width: "100%",
    height: "100%",
});
export const portraitAreaStatus = style({
    width: "auto",
    background: "rgba(100, 100, 100, 0.5)",
    color: "white",
    position: "absolute",
    padding: "0px 0px 0px 3px",
    fontSize: "0.7rem",
    left: "5px",
    top: "5px",
    borderRadius: "2px",
});
export const portraitAreaStatusVctype = style({
    fontWeight: "800",
    color: "#866",
});
export const portraitAreaTermsOfUse = style({
    width: "5rem",
    background: "rgba(100, 100, 100, 0.5)",
    color: "white",
    position: "absolute",
    padding: "2px",
    fontSize: "0.6rem",
    right: "5px",
    bottom: "5px",
});
export const portraitAreaAboutModelAndVoice = style({
    display: "flex",
    flexDirection: "column",
    // width: "8rem",
    background: "rgba(100, 100, 100, 0.5)",
    color: "white",
    position: "absolute",
    padding: "2px",
    fontSize: "0.6rem",
    right: "5px",
    bottom: "5px",
});

export const portraitAreaAboutModelAndVoicePopupLink = style({
    color: "blue",
    cursor: "pointer",
    textDecoration: "underline",
});

export const characterAreaControlArea = style({
    display: "flex",
    flexDirection: "column",
    gap: "10px",
    width: "30rem",
});
export const characterAreaControl = style({
    display: "flex",
    gap: "3px",
    alignItems: "center",
});
export const characterAreaControlTitle = style({
    width: "6rem",
    fontWeight: "700",
});
export const characterAreaControlField = style({
    display: "flex",
    flexDirection: "column",
});
export const characterAreaControlFieldFullWidth = style({
    display: "flex",
    flexDirection: "column",
    width: "100%",
});
export const characterAreaControlOperationButtons = style({
    display: "flex",
    flexDirection: "row",
    width: "100%",
    gap: "10px",
    justifyContent: "center",
});
export const characterAreaControlOperationButton = style({
    width: "5rem",
    border: "solid 1px #999",
    borderRadius: "4px",
    background: "#ddd",
    cursor: "pointer",
    fontWeight: "700",
    textAlign: "center",
    ":hover": {
        border: "solid 1px #000",
    },
});

export const characterAreaText = style({
    fontSize: "0.9rem",
});
export const characterAreaControlButtonActive = style({
    width: "5rem",
    border: "solid 1px #333",
    borderRadius: "2px",
    background: "#ada",
    fontWeight: "700",
    textAlign: "center",
});
export const characterAreaControlButtonStanby = style({
    width: "5rem",
    border: "solid 1px #999",
    borderRadius: "2px",
    background: "#aba",
    cursor: "pointer",
    fontWeight: "700",
    textAlign: "center",
    ":hover": {
        border: "solid 1px #000",
    },
});
export const characterAreaControlPassthruButtonStanby = style({
    width: "5rem",
    border: "solid 1px #999",
    borderRadius: "7px",
    padding: "2px",
    background: "#aba",
    cursor: "pointer",
    fontWeight: "700",
    fontSize: "0.8rem",
    textAlign: "center",
    ":hover": {
        border: "solid 1px #000",
    },
});
export const characterAreaControlPassthruButtonActive = style({
    width: "5rem",
    border: "solid 1px #955",
    borderRadius: "7px",
    padding: "2px",
    background: "#fdd",
    cursor: "pointer",
    fontWeight: "700",
    fontSize: "0.8rem",
    textAlign: "center",
    ":hover": {
        border: "solid 1px #000",
    },
});
export const characterAreaControlButtons = style({
    display: "flex",
    flexDirection: "row",
    gap: "10px",
});
export const characterAreaSliderControl = style({
    display: "flex",
    flexDirection: "row",
    gap: "5px",
});
export const characterAreaSliderControlKind = style({
    width: "3rem",
});
export const characterAreaSliderControlSlider = style({
    width: "10rem",
});

export const characterAreaSliderControlVal = style({
    width: "3rem",
});

export const beatricePortraitTitle = style({
    fontSize: "1rem",
    fontWeight: "700",
    color: "#333",
    textShadow: "0 0 2px #333",
    textAlign: "center",
});
export const beatricePortraitTitleEdition = style({
    fontSize: "0.6rem",
});

export const beatricePortraitSelect = style({
    display: "flex",
    justifyContent: "center",
});
export const beatricePortraitSelectButton = style({
    color: "#615454",
    fontWeight: "700",
    fontSize: "0.8rem",
    borderRadius: "2px",
    background: "#adafad",
    cursor: "pointer",
    padding: "0px 5px 0px 5px",
    margin: "0px 5px 0px 5px",
    lineHeight: "140%",
    height: "1.1rem",
});
export const beatricePortraitSelectButtonSelected = style({
    color: "#615454",
    fontWeight: "700",
    fontSize: "0.8rem",
    borderRadius: "2px",
    background: "#62b574",
    cursor: "pointer",
    padding: "0px 5px 0px 5px",
    margin: "0px 5px 0px 5px",
    lineHeight: "140%",
    height: "1.1rem",
});

export const beatriceSpeakerGraphContainer = style({
    width: "20rem",
    height: "19rem",
    border: "none",
});
