import { useEffect, useRef } from "react";

import { LOADING_MESSAGE } from "../constants";
import type { ChatMessage } from "../types";
import { AbstentionCard } from "./AbstentionCard";
import { AnswerCard } from "./AnswerCard";
import { ErrorCard } from "./ErrorCard";

interface MessageListProps {
    messages: ChatMessage[];
    isWaiting: boolean;
    onRetry: (question: string) => void;
}

interface MessageItemProps {
    message: ChatMessage;
    isWaiting: boolean;
    onRetry: (question: string) => void;
}

function MessageItem({ message, isWaiting, onRetry }: MessageItemProps) {
    switch (message.kind) {
        case "question":
            return <div className="message question">{message.text}</div>;
        case "answer":
            return message.answer.abstained
                ? <AbstentionCard answer={message.answer} />
                : <AnswerCard answer={message.answer} />;
        case "error":
            return <ErrorCard code={message.code} question={message.question} onRetry={onRetry} isWaiting={isWaiting} />;
    }
}

export function MessageList({ messages, isWaiting, onRetry }: MessageListProps) {
    const listEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        listEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [messages, isWaiting]);

    return (
        <div className="message-list" aria-live="polite">
            {messages.map((message, index) => (
                <MessageItem key={index} message={message} isWaiting={isWaiting} onRetry={onRetry} />
            ))}
            {isWaiting && (
                <div className="message loading">
                    <span className="typing-dots" aria-hidden="true">
                        <span />
                        <span />
                        <span />
                    </span>
                    {LOADING_MESSAGE}
                </div>
            )}
            <div ref={listEndRef} />
        </div>
    );
}
