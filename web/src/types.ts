export type Reliability = "high" | "medium";

export interface Citation {
    document: string;
    section: string;
    text: string;
    title: string | null;
    paragraph: string | null;
}

export interface Answer {
    abstained: boolean;
    text: string | null;
    reliability: Reliability | null;
    citations: Citation[];
}

export type ErrorCode =
    | "usage_limit"
    | "model_login"
    | "model_error"
    | "invalid_question"
    | "internal_error"
    | "server_unreachable";

export interface ErrorDescription {
    title: string;
    detail: string;
    canRetry: boolean;
}

export type ChatMessage =
    | { kind: "question"; text: string }
    | { kind: "answer"; answer: Answer }
    | { kind: "error"; code: ErrorCode; question: string };
