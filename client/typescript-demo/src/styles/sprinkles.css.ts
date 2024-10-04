import { defineProperties, createSprinkles } from "@vanilla-extract/sprinkles";

const properties = defineProperties({
    properties: {
        display: ["none", "block", "flex"],
        padding: ["0", "8px", "16px"],
    },
});

export const sprinkles = createSprinkles(properties);
