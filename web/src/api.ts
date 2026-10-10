import { ASK_ENDPOINT } from "./constants";
import type { Answer } from "./types";

export async function fetchAnswer(question: string): Promise<Answer> {
    const response = await fetch(ASK_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
    });
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
}
