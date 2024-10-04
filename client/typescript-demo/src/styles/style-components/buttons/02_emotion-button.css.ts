import { recipe } from '@vanilla-extract/recipes'

export const Emotion = {
    anger: {
        background: "#ffdede"
    },
    disgust: {
        background: "#bee0ec"
    },
    fear: {
        background: "#f2e9ff"
    },
    happy: {
        background: "#f4ff00"
    },
    sad: {
        background: "#e2e9f7"
    },
    surprise: {
        background: "#f1e687"
    },
    other: {
        background: "#aeaaaa"
    },
    none: {
        background: "#ffffff"
    },
} as const
export type Emotion = keyof typeof Emotion


export const EmotionButton = recipe({
    base: {
        borderRadius: "3px",
        textAlign: 'center',
        fontSize: '0.7rem',
        height: "1rem",
        width: "4rem",
        border: "solid 2px grey",
        cursor: 'pointer',
        ":hover": {
            border: `solid 2px darkgrey`,
        },
    },
    variants: {
        emotion: Emotion
    }
})


export const EmotionBlockButton = recipe({
    base: {
        width: "14px",
        height: "14px",
        borderRadius: "3px",
        cursor: 'pointer',
        ":hover": {
            border: `solid 2px darkgrey`,
        },
    },
    variants: {
        emotion: Emotion,
        selected: {
            true: {
                borderColor: "red",
                borderWidth: "3px",
                borderStyle: "solid"
            },
            false: {
                borderColor: "grey",
                borderWidth: "1px",
                borderStyle: "solid",
            }
        }
    }
}
)
