import type { Reliability } from "./types";

export const BRAND_MARK = "§";
export const PAGE_TITLE = "Tanulmányi kérdések";
export const PAGE_SUBTITLE = "Válaszok a BME szabályzataiból, a forrás megjelölésével";
export const WELCOME_TITLE = "Miben segíthetek?";
export const INTRO_TEXT =
    "Kérdezz a BME tanulmányi szabályzatairól! Minden válasz mellett látod, melyik § alapján született.";
export const EXAMPLES_LABEL = "Próbáld ki például:";
export const EXAMPLE_QUESTIONS = [
    "Meddig kell beadnom a vendéghallgatói kérelmet?",
    "Kell fizetnem, ha vendéghallgatóként veszek fel tárgyat?",
    "Hány kreditet teljesíthetek részismereti képzésben?",
];
export const QUESTION_LABEL = "Kérdés";
export const QUESTION_PLACEHOLDER = "Írd be a kérdésed…";
export const SEND_BUTTON_LABEL = "Küldés";
export const DISCLAIMER_TEXT =
    "Tájékoztató jellegű, a szabályzat szövege az irányadó. Hallgatói projekt, nem hivatalos egyetemi szolgáltatás.";

export const ASK_ENDPOINT = "/ask";
export const LOADING_MESSAGE = "Keresem a választ…";
export const ERROR_MESSAGE = "Nem sikerült választ kapni. Próbáld újra!";

export const RELIABILITY_LABELS: Record<Reliability, string> = {
    high: "Megbízhatóság: magas",
    medium: "Megbízhatóság: közepes – érdemes ellenőrizni a hivatkozott szöveget",
};
export const CITATIONS_HEADING = "Források";
export const ABSTENTION_NOTICE = "Erre a szabályzatok nem adnak egyértelmű választ.";
export const ABSTENTION_REFERRAL = "Fordulj az illetékes kar Dékáni Hivatalához.";
export const RELATED_CITATIONS_HEADING = "Ami esetleg kapcsolódik:";
