import { keyframes, style } from "@vanilla-extract/css";
import { globaVars } from "./001_global.css";

const dialogContainerShowAnimation = keyframes({
    from: {
        opacity: "0",
        zIndex: "-1",
    },
    "10%": {
        zIndex: "200",
    },
    to: {
        opacity: "1",
        zIndex: "200",
    },
});
const dialogContainerHideAnimation = keyframes({
    from: {
        opacity: "1",
        zIndex: "200",
    },
    "90%": {
        zIndex: "200",
    },
    to: {
        opacity: "0",
        zIndex: "-1",
    },
});

export const dialogContainer = style({
    justifyContent: "center",
    alignItems: "center",
    position: "absolute",
    top: "0px",
    left: "0px",
    width: "100vw",
    height: "100vh",
    zIndex: "-1",
    display: "flex",

    background: "rgba(100, 100, 100, 0.4)",
    animationName: dialogContainerHideAnimation,
    animationDuration: "0.4s",
    animationIterationCount: "1",
    animationFillMode: "forwards",
    animationDirection: "normal",
});

export const dialogContainerShow = style({
    background: "rgba(200, 200, 200, 0.4)",
    animationName: dialogContainerShowAnimation,
});

const dialog2ContainerShowAnimation = keyframes({
    from: {
        opacity: "0",
        zIndex: "-1",
    },
    "10%": {
        zIndex: "400",
    },
    to: {
        opacity: "1",
        zIndex: "400",
    },
});
const dialog2ContainerHideAnimation = keyframes({
    from: {
        opacity: "1",
        zIndex: "400",
    },
    "90%": {
        zIndex: "400",
    },
    to: {
        opacity: "0",
        zIndex: "-1",
    },
});

export const dialog2Container = style({
    justifyContent: "center",
    alignItems: "center",
    position: "absolute",
    top: "0px",
    left: "0px",
    width: "100vw",
    height: "100vh",
    zIndex: "-1",
    display: "flex",

    background: "rgba(100, 100, 100, 0.4)",
    animationName: dialog2ContainerHideAnimation,
    animationDuration: "0.4s",
    animationIterationCount: "1",
    animationFillMode: "forwards",
    animationDirection: "normal",
});

export const dialog2ContainerShow = style({
    background: "rgba(200, 200, 200, 0.4)",
    animationName: dialog2ContainerShowAnimation,
});

export const dialogFrame = style({
    color: globaVars.color.companyColor2,
    width: "40rem",
    maxHeight: "80vh",
    border: `2px solid ${globaVars.color.dialogBorderColor}`,
    borderRadius: "20px",
    flexDirection: "column",
    alignItems: "center",
    boxShadow: `5px 5px 5px ${globaVars.color.dialogShadowColor}`,
    background: globaVars.color.dialogBackgroundColor,
    overflow: "hidden",
    display: "flex",
});

export const dialogTitle = style({
    marginTop: "20px",
    background: globaVars.color.companyColor2,
    color: "#fff",
    width: "100%",
    textAlign: "center",
});

export const dialogFixedSizeContent = style({
    width: "90%",
    maxHeight: "70vh",
});

export const modelSlotContainer = style({
    maxHeight: "60vh",
    width: "100%",
    overflowY: "scroll",
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
export const sampleSlotContainer = modelSlotContainer;

export const modelSlot = style({
    height: "5rem",
    display: "flex",
    flexDirection: "row",
});
export const sampleSlot = modelSlot;

export const modelSlotDetailArea = style({
    display: "flex",
    flexDirection: "column",
    fontSize: "0.8rem",
    borderBottom: "solid 1px #aaa",
    width: "80%",
    overflowY: "scroll",
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
export const modelSampleDetailArea = modelSlotDetailArea;

export const modelSlotIconPointable = style({
    width: "5rem",
    height: "5rem",
    cursor: "pointer",
});
export const modelSlotIcon = style({
    width: "5rem",
    height: "5rem",
});
export const modelSampleIcon = modelSlotIcon;

export const modelSlotDetailRow = style({
    display: "flex",
    flexDirection: "row",
});
export const modelSampleDetailRow = modelSlotDetailRow;

export const modelSlotDetailRowLabel = style({
    width: "20%",
    whiteSpace: "nowrap",
});
export const modelSampleDetailRowLabel = modelSlotDetailRowLabel;

export const modelSlotDetailRowValuePointable = style({
    width: "55%",
    whiteSpace: "nowrap",
    cursor: "pointer",
});

export const modelSlotDetailRowValue = style({
    width: "55%",
    whiteSpace: "nowrap",
});
export const modelSampleDetailRowValue = modelSlotDetailRowValue;

export const modelSlotDetailRowValueSmall = style({
    color: "rgb(30, 30, 30)",
    fontSize: "0.7rem",
});
export const modelSampleDetailRowValueSmall = modelSlotDetailRowValueSmall;

export const modelSlotDetailRowValueWrap = style({
    width: "55%",
});

export const modelSlotButtonsArea = style({
    display: "flex",
    flexDirection: "column",
    borderBottom: "solid 1px #a00",
    width: "20%",
    fontSize: "0.8rem",
    padding: "4px",
});
export const modelSampleButtonsArea = modelSlotButtonsArea;

export const modelSlotButton = style({
    border: "solid 1px #999",
    borderRadius: "2px",
    cursor: "pointer",
    verticalAlign: "middle",
    textAlign: "center",
    padding: "1px",
    ":hover": {
        border: "solid 1px #000",
    },
});
export const sampleSlotButton = modelSlotButton;

export const closeButtonRow = style({
    width: "100%",
    display: "flex",
    justifyContent: "center",
    gap: "2rem",
});
export const closeButton = style({
    border: "solid 1px #999",
    borderRadius: "2px",
    cursor: "pointer",
    textAlign: "center",
    margin: "10px 0px 10px 0px",
    padding: "0px 15px 0px 15px",
    ":hover": {
        border: "solid 1px #000",
    },
});
export const execButton = style({
    border: "solid 1px #999",
    borderRadius: "2px",
    cursor: "pointer",
    textAlign: "center",
    margin: "10px 0px 10px 0px",
    padding: "0px 15px 0px 15px",
    ":hover": {
        border: "solid 1px #000",
    },
});

export const instructions = style({
    fontSize: "1rem",
    padding: "20px",
    textAlign: "center",
});

export const assertion = style({
    fontSize: "1rem",
    padding: "2px",
    textAlign: "center",
    color: "red",
    fontWeight: 700,
});

export const textInputArea = style({
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    padding: "2px 0px 20px 0px",
});
export const textInputAreaLabel = style({});
export const textInputAreaInput = style({});

export const selectInputArea = style({
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    padding: "2px 0px 20px 0px",
});
export const selectInputAreaLabel = style({});
export const selectInputAreaInput = style({});
export const uploadStatusArea = style({
    height: "1rem",
    textAlign: "center",
});
export const fileInputArea = style({
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    padding: "2px 0px 2px 0px",
});
export const fileInputAreaLabel = style({
    width: "7rem",
});
export const fileInputAreaValue = style({
    width: "25rem",
});
export const fileInputAreaButton = style({
    width: "7rem",
    border: "solid 1px #999",
    borderRadius: "2px",
    cursor: "pointer",
    textAlign: "center",
    ":hover": {
        border: "solid 1px #000",
    },
});

export const dialogItemRow = style({
    display: "flex",
    flexDirection: "row",
    width: "100%",
    padding: "2px",
});

export const dialogItemName10 = style({
    fontWeight: 700,
    width: "10rem",
    padding: "2px",
});
export const dialogItemName20 = style({
    fontWeight: 700,
    width: "20rem",
    padding: "2px",
});
export const dialogItemName30 = style({
    fontWeight: 700,
    width: "30rem",
    padding: "2px",
});

export const dialogItemValue = style({
    width: "10rem",
    padding: "2px",
});

export const dialogItemValueSliderContainer = style({
    display: "flex",
    flexDirection: "row",
    gap: "5px",
});

export const dialogItemValueSlider = style({
    width: "10rem",
});
export const dialogItemValueSliderVal = style({
    width: "3rem",
});

export const dialogMergeLabFilterRow = style({
    display: "flex",
    flexDirection: "row",
    width: "100%",
    gap: "10px",
});
export const dialogMergeLabBlendArea = style({
    display: "flex",
    flexDirection: "row",
    width: "100%",
    gap: "10px",
    marginTop: "2rem",
});

export const dialogMergeLabBlendAreaModelListContainer = style({
    display: "flex",
    flexDirection: "column",
    width: "30rem",
    gap: "3px",
    height: "20rem",
    overflowY: "scroll",
});
export const dialogMergeLabBlendAreaModelList = style({
    display: "flex",
    flexDirection: "column",
    width: "30rem",
    gap: "3px",
});
export const dialogMergeLabBlendAreaControl = style({
    display: "flex",
    flexDirection: "column",
    width: "10rem",
    gap: "10px",
});
export const dialogMergeLabBlendAreaControlSlotSelect = style({
    display: "flex",
    flexDirection: "row",
    width: "10rem",
});
export const dialogMergeLabBlendAreaControlAssertion = style({
    display: "flex",
    flexDirection: "row",
    width: "7rem",
    fontSize: "0.8rem",
    fontWeight: 700,
    color: "red",
});

export const dialogMergeLabBlendAreaControlMergeButtonContainer = style({
    display: "flex",
    flexDirection: "row",
    width: "7rem",
});

export const dialogMergeLabBlendAreaControlMergeButton = style({
    width: "7rem",
    border: "solid 1px #999",
    borderRadius: "2px",
    cursor: "pointer",
    textAlign: "center",
    ":hover": {
        border: "solid 1px #000",
    },
});

export const dialogMergeLabBlendAreaModelListItem = style({
    display: "flex",
    width: "100%",
});

export const dialogMergeLabBlendAreaModelListItemIndex = style({
    width: "2rem",
});
export const dialogMergeLabBlendAreaModelListItemName = style({
    width: "10rem",
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
});
export const dialogMergeLabBlendAreaModelListItemRange = style({
    width: "10rem",
});
export const dialogMergeLabBlendAreaModelListItemValue = style({
    width: "3rem",
});

export const dialogNotice = style({});
export const dialogNoticeLinkArea = style({
    margin: "1rem 1rem 1rem 3rem",
});
export const dialogDonateLinkSpan = style({
    color: "blue",
    cursor: "pointer",
    textDecoration: "underline",
});
export const dialogDonateLinkSpanImg = style({
    borderRadius: "50px",
    height: "3rem",
});

export const aboutModelModelName = style({
    fontSize: "1rem",
    fontWeight: 700,
    color: "#333",
});
export const aboutModelModelDescription = style({
    fontSize: "0.8rem",
    color: "#333",
});
export const aboutModelModelDescriptionPre = style({
    whiteSpace: "pre-wrap",
    userSelect: "text",
});
