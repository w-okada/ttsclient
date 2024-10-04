import { style } from "@vanilla-extract/css";

export const configArea = style({
    display: "flex",
    flexDirection: "column",
    gap: "1.5rem",
    padding: "10px",
});
export const configAreaRow = style({
    display: "flex",
    flexDirection: "row",
    gap: "1rem",
});
export const configSubArea = style({
    display: "flex",
    flexDirection: "column",
    gap: "0.3rem",
    width: "20rem",
});
export const configSubAreaLong = style({
    display: "flex",
    flexDirection: "column",
    gap: "0.3rem",
    width: "40rem",
});

export const configSubAreaRow = style({
    display: "flex",
    width: "100%",
});
export const configSubAreaRowTitle4 = style({
    width: "4rem",
    fontWeight: "700",
});
export const configSubAreaRowTitle5 = style({
    width: "5rem",
    fontWeight: "700",
});
export const configSubAreaRowTitle7 = style({
    width: "7rem",
    fontWeight: "700",
});

export const configSubAreaRowTitle10 = style({
    width: "10rem",
    fontWeight: "700",
});

export const configSubAreaRowTitle20 = style({
    width: "20rem",
    fontWeight: "700",
});
export const configSubAreaRowField12 = style({
    width: "12rem",
    display: "flex",
    justifyContent: "center",
    flexDirection: "column",
});
export const configSubAreaRowField14 = style({
    width: "14rem",
    display: "flex",
    justifyContent: "center",
    flexDirection: "column",
});
export const configSubAreaRowField15 = style({
    width: "15rem",
    display: "flex",
    justifyContent: "center",
    flexDirection: "column",
});
export const configSubAreaRowField30 = style({
    width: "30rem",
    display: "flex",
    justifyContent: "center",
    flexDirection: "column",
});
export const configSubAreaButtonContainer = style({
    display: "flex",
    gap: "5px",
    flexWrap: "wrap",
});
export const configSubAreaButtonContainerCheckbox = style({
    display: "flex",
    gap: "5px",
});
export const configSubAreaButtonContainerButton = style({
    border: "solid 2px #999",
    color: "white",
    background: "#666",

    cursor: "pointer",

    fontSize: "0.8rem",
    borderRadius: "5px",
    height: "1.2rem",
    paddingLeft: "2px",
    paddingRight: "2px",
    textAlign: "center",
    ":hover": {
        border: "solid 2px #faa",
    },
});
export const configSubAreaButtonContainerButtonActive = style({
    background: "#844",
    cursor: "default",
});

export const configSubAreaSliderControl = style({
    display: "flex",
    flexDirection: "row",
    width: "100%",
});
export const configSubAreaSliderControlKind = style({
    width: "10%",
});
export const configSubAreaSliderControlSlider = style({
    width: "70%",
    display: "flex",
});
export const configSubAreaSliderControlSliderInput = style({
    width: "100%",
});
export const configSubAreaSliderControlVal = style({
    width: "20%",
});
export const configSubAreaControlFieldWavFile = style({
    display: "flex",
    flexDirection: "row",
    gap: "5px",
    width: "100%",
});
export const configSubAreaControlFieldWavFileAudioContainer = style({
    height: "1rem",
    width: "100%",
});
export const configSubAreaControlFieldWavFileAudio = style({
    height: "1rem",
    width: "100%",
});
export const configSubAreaInputMediaContainer = style({
    display: "flex",
    width: "100%",
    justifyContent: "flex-end",
});
export const configSubAreaInputMedia = style({
    height: "1rem",
    width: "15rem",
});
export const configSubAreaInputMediaFileSelectIcon = style({
    height: "1rem",
    width: "2rem",
});
export const configSubAreaInputMediaCaptureButton = style({
    fontSize: "0.8rem",
    border: "solid 1px #333",
    borderRadius: "5px",
    background: "#fff",
    height: " 1.2rem",
    paddingLeft: "2px",
    paddingRight: "2px",
    cursor: "pointer",
    width: "4rem",
    textAlign: "center",
    ":hover": {
        border: "solid 1px #aaa",
        fontWeight: "700",
    },
});
export const configSubAreaInputMediaCaptureButtonActive = style({
    fontSize: "0.8rem",
    border: "solid 1px #333",
    borderRadius: "5px",
    background: "#ada",
    height: " 1.2rem",
    paddingLeft: "2px",
    paddingRight: "2px",
    cursor: "pointer",
    width: "4rem",
    textAlign: "center",
    ":hover": {
        border: "solid 1px #aaa",
        fontWeight: "700",
    },
});
export const configSubAreaInputMediaEchoButton = style({
    fontSize: "0.8rem",
    border: "solid 1px #333",
    borderRadius: "5px",
    background: "#fff",
    height: " 1.2rem",
    paddingLeft: "2px",
    paddingRight: "2px",
    cursor: "pointer",
    width: "4rem",
    textAlign: "center",
    ":hover": {
        border: "solid 1px #aaa",
        fontWeight: "700",
    },
});
export const configSubAreaInputMediaEchoButtonActive = style({
    fontSize: "0.8rem",
    border: "solid 1px #333",
    borderRadius: "5px",
    background: "#ada",
    height: " 1.2rem",
    paddingLeft: "2px",
    paddingRight: "2px",
    cursor: "pointer",
    width: "4rem",
    textAlign: "center",
});

export const textAlignRight = style({
    textAlign: "right",
});
