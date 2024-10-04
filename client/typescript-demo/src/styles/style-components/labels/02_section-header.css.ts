

import { recipe } from '@vanilla-extract/recipes'


export const SectionHeader = recipe({
    base: {
        fontSize: "1.4rem",
        fontWeight: "700",
        color: "#666666"
    },
    variants: {
        paddingLeft: {
            "0rem": {
                paddingLeft: "0rem"
            },
            "1rem": {
                paddingLeft: "1rem"
            },
            "2rem": {
                paddingLeft: "2rem"
            }
        },
        width: {
            small: {
                width: '4rem',
            },
            medium: {
                width: '6rem',
            },
            large: {
                width: '8rem',
            },
            "x-large": {
                width: '20rem',
            }
        },
    },

    defaultVariants: {
        paddingLeft: "0rem",
        width: "x-large",
    }
}
)
