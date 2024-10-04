import { recipe } from '@vanilla-extract/recipes'
import { buttonThemeContract } from './thema/button-thema.css'


export const BasicButton = recipe({
    base: {
        textAlign: 'center',
        paddingTop: '0.1rem',
        width: '5rem',
        height: '1.5rem',
        fontSize: '0.8rem',
        borderRadius: buttonThemeContract.border.radius,
        cursor: 'pointer',
    },
    variants: {
        active: {
            true: {
                color: buttonThemeContract.color.textActive,
                backgroundColor: buttonThemeContract.color.backgroundActive,
                border: `solid ${buttonThemeContract.border.width} ${buttonThemeContract.color.borderActive}`,
                ":hover": {
                    color: buttonThemeContract.color.textHover,
                    backgroundColor: buttonThemeContract.color.backgroundHover,
                    border: `solid ${buttonThemeContract.border.width} ${buttonThemeContract.color.borderHover}`,
                },

            },
            false: {
                color: buttonThemeContract.color.text,
                backgroundColor: buttonThemeContract.color.background,
                border: `solid ${buttonThemeContract.border.width} ${buttonThemeContract.color.border}`,
                ":hover": {
                    color: buttonThemeContract.color.textHover,
                    backgroundColor: buttonThemeContract.color.backgroundHover,
                    border: `solid ${buttonThemeContract.border.width} ${buttonThemeContract.color.borderHover}`,
                },
            },
        },
        width: {
            small: {
                width: '3rem',
            },
            medium: {
                width: '5rem',
            },
            large: {
                width: '7rem',
            },
        },
    },

    defaultVariants: {
        active: false,
        width: "medium",
    }
}
)
