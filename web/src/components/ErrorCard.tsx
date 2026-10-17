import { ERROR_MESSAGES, RETRY_BUTTON_LABEL } from "../constants";
import type { ErrorCode } from "../types";
import { AlertIcon } from "./icons";

interface ErrorCardProps {
    code: ErrorCode;
    question: string;
    onRetry: (question: string) => void;
    isWaiting: boolean;
}

export function ErrorCard({ code, question, onRetry, isWaiting }: ErrorCardProps) {
    const description = ERROR_MESSAGES[code];
    return (
        <article className="message error" role="alert">
            <div className="notice">
                <AlertIcon />
                <div>
                    <p className="notice-title">{description.title}</p>
                    <p className="notice-detail">{description.detail}</p>
                    {description.canRetry && (
                        <button type="button" className="retry-button" onClick={() => onRetry(question)} disabled={isWaiting}>
                            {RETRY_BUTTON_LABEL}
                        </button>
                    )}
                </div>
            </div>
        </article>
    );
}
