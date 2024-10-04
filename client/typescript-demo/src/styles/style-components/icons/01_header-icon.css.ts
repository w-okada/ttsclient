import { recipe } from "@vanilla-extract/recipes";
import { globaVars, lightTheme } from "../../001_global.css";

export const HeaderIcon = recipe({
    base: {
        background: globaVars.color.backgroundLightMode,
        borderRadius: "1rem",
        height: "1.5rem",
    },

}
)