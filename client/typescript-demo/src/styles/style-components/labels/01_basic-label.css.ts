

import { recipe } from '@vanilla-extract/recipes'


export const BasicLabel = recipe({
    base: {
        fontWeight: "700",
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
        width: "medium",
    }
}
)
