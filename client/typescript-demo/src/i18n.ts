import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import Backend from "i18next-http-backend";


export const setupI18n = (i18nPath: string) => {
    i18n.use(Backend)
        .use(LanguageDetector)
        .use(initReactI18next)
        .init({
            backend: {
                loadPath: i18nPath,
            },
            fallbackLng: "en",
            interpolation: {
                escapeValue: false,
            },
        });
}

