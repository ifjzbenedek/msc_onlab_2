export type Reliability = "high" | "medium";

export interface Citation {
    document: string;
    section: string;
    text: string;
    paragraph: string | null;
}

export interface Answer {
    abstained: boolean;
    text: string | null;
    reliability: Reliability | null;
    citations: Citation[];
}

export type ChatMessage =
    | { kind: "question"; text: string }
    | { kind: "answer"; answer: Answer }
    | { kind: "error"; text: string };
