import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import ar from "./ar.json";
import en from "./en.json";

const stored = localStorage.getItem("faith-lang");
const initial = stored === "en" || stored === "ar" ? stored : "ar";

void i18n.use(initReactI18next).init({
  resources: { ar: { translation: ar }, en: { translation: en } },
  lng: initial,
  fallbackLng: "ar",
  interpolation: { escapeValue: false },
});

// يضبط اتجاه الصفحة يميناً للعربية ويساراً للإنجليزية.
export function applyDirection(language: string) {
  const lang = language.startsWith("en") ? "en" : "ar";
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  localStorage.setItem("faith-lang", lang);
}

applyDirection(initial);
i18n.on("languageChanged", applyDirection);

export default i18n;
