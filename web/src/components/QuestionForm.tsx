import { useEffect, useRef, useState, type FormEvent } from "react";

import { QUESTION_LABEL, QUESTION_PLACEHOLDER, SEND_BUTTON_LABEL } from "../constants";
import { SendIcon } from "./icons";

interface QuestionFormProps {
    onAsk: (question: string) => void;
    isWaiting: boolean;
}

export function QuestionForm({ onAsk, isWaiting }: QuestionFormProps) {
    const [question, setQuestion] = useState("");
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (!isWaiting) {
            inputRef.current?.focus();
        }
    }, [isWaiting]);

    function submitQuestion(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const trimmedQuestion = question.trim();
        if (!trimmedQuestion) {
            return;
        }
        onAsk(trimmedQuestion);
        setQuestion("");
    }

    return (
        <form className="question-form" onSubmit={submitQuestion}>
            <input
                ref={inputRef}
                type="text"
                aria-label={QUESTION_LABEL}
                placeholder={QUESTION_PLACEHOLDER}
                autoComplete="off"
                required
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                disabled={isWaiting}
            />
            <button type="submit" className="send-button" aria-label={SEND_BUTTON_LABEL} disabled={isWaiting}>
                <SendIcon />
            </button>
        </form>
    );
}
