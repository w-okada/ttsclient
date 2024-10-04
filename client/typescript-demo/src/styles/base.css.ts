import { style } from "@vanilla-extract/css";


export const left1Padding = style({
    paddingLeft: "1rem",
});
export const left3Padding = style({
    paddingLeft: "3rem",
});

export const loggerDiv = style({
    userSelect: "text",
    width: "100%",
    height: "100%",
});
export const loggerArea = style({
    height: "80%",
    overflowY: "scroll",
});
export const logLine = style({
    whiteSpace: "nowrap",
});
export const decoratedWordRed = style({
    color: "red",
    fontWeight: 700,
});
export const decoratedWordBlue = style({
    color: "blue",
    fontWeight: 700,
});
export const decoratedWordGreen = style({
    color: "green",
    fontWeight: 700,
});

export const loggerControlArea = style({
    height: "3rem",
    marginTop: "1rem",
});
export const loggerControlButton = style({
    width: "3rem",
    margin: "0.5rem",
    background: "rgba(255, 255, 255, 0.5)",
});

export const errorBoundaryContainer = style({
    display: "flex",
    flexDirection: "column",
    alignItems: "start",
    justifyContent: "center",
    height: "100vh",
    userSelect: "text",
    gap: "0.5rem",
});

export const errorBoundaryTitle = style({
    fontSize: "1.5rem",
});
export const errorBoundaryName = style({
    fontSize: "1.2rem",
});

export const errorBoundaryMessage = style({
    fontSize: "1.2rem",
});
export const errorBoundaryInfo = style({
    fontSize: "1rem",
});

export const spacer_h10px = style({
    height: "10px",
});
