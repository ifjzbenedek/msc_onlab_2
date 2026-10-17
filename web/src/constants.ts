import type { ErrorCode, ErrorDescription, Reliability } from "./types";

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
export const HEALTH_ENDPOINT = "/health";
export const HEALTH_CHECK_INTERVAL_MS = 5000;
export const LOADING_MESSAGE = "Keresem a választ…";

export const SERVER_UNREACHABLE_ERROR: ErrorCode = "server_unreachable";
export const INTERNAL_ERROR: ErrorCode = "internal_error";
export const RETRY_BUTTON_LABEL = "Újrapróbálom";
export const ERROR_MESSAGES: Record<ErrorCode, ErrorDescription> = {
    usage_limit: {
        title: "Most nem tudok válaszolni",
        detail: "Elfogyott a nyelvi modell használati kerete. Később próbáld újra.",
        canRetry: true,
    },
    model_login: {
        title: "A nyelvi modell nem érhető el",
        detail: "A szerveren nincs érvényes bejelentkezés a nyelvi modellhez. Ezt a szerver üzemeltetőjének kell rendeznie.",
        canRetry: false,
    },
    model_error: {
        title: "Nem sikerült megírni a választ",
        detail: "A nyelvi modell hívása hibával tért vissza. Érdemes újrapróbálni.",
        canRetry: true,
    },
    invalid_question: {
        title: "Ezt a kérdést nem tudom feldolgozni",
        detail: "A kérdés üres vagy hibás formátumú. Írd be újra.",
        canRetry: false,
    },
    internal_error: {
        title: "Váratlan hiba történt",
        detail: "A válasz készítése közben hiba történt a szerveren. Próbáld újra; ha ismétlődik, a részletek a szerver naplójában vannak.",
        canRetry: true,
    },
    server_unreachable: {
        title: "Nem érem el a szervert",
        detail: "Lehet, hogy a szerver nem fut, vagy még a modelleket tölti be. Próbáld újra egy kicsit később.",
        canRetry: true,
    },
};
export const CONNECTION_LOST_TITLE = "A szerver most nem érhető el";
export const CONNECTION_LOST_DETAIL =
    "Ha most indult el, valószínűleg még a modelleket tölti be. Néhány másodpercenként újrapróbálom.";

export const RELIABILITY_LABELS: Record<Reliability, string> = {
    high: "Megbízhatóság: magas",
    medium: "Megbízhatóság: közepes – érdemes ellenőrizni a hivatkozott szöveget",
};
export const CITATIONS_HEADING = "Források";
export const ABSTENTION_NOTICE = "Erre a szabályzatok nem adnak egyértelmű választ.";
export const ABSTENTION_REFERRAL = "Fordulj az illetékes kar Dékáni Hivatalához.";
export const RELATED_CITATIONS_HEADING = "Ami esetleg kapcsolódik:";
