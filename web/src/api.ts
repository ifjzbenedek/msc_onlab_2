import { ASK_ENDPOINT, ERROR_MESSAGES, HEALTH_ENDPOINT, INTERNAL_ERROR, SERVER_UNREACHABLE_ERROR } from "./constants";
import type { Answer, ErrorCode } from "./types";

export class AskError extends Error {
    code: ErrorCode;

    constructor(code: ErrorCode) {
        super(code);
        this.code = code;
    }
}

function isErrorCode(value: unknown): value is ErrorCode {
    return typeof value === "string" && Object.hasOwn(ERROR_MESSAGES, value);
}

async function readErrorCode(response: Response): Promise<ErrorCode> {
    try {
        const body = await response.json();
        return isErrorCode(body.error) ? body.error : INTERNAL_ERROR;
    } catch {
        return SERVER_UNREACHABLE_ERROR;
    }
}

export async function fetchAnswer(question: string): Promise<Answer> {
    let response: Response;
    try {
        response = await fetch(ASK_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });
    } catch {
        throw new AskError(SERVER_UNREACHABLE_ERROR);
    }
    if (!response.ok) {
        throw new AskError(await readErrorCode(response));
    }
    return response.json();
}

export async function checkBackendHealth(): Promise<boolean> {
    try {
        const response = await fetch(HEALTH_ENDPOINT);
        return response.ok;
    } catch {
        return false;
    }
}
