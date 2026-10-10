import { useEffect, useRef } from "react";

import { LOADING_MESSAGE } from "../constants";
import type { ChatMessage } from "../types";
import { AbstentionCard } from "./AbstentionCard";
import { AnswerCard } from "./AnswerCard";

interface MessageListProps {
    messages: ChatMessage[];
    isWaiting: boolean;
}

interface MessageItemProps {
    message: ChatMessage;
}

function MessageItem({ message }: MessageItemProps) {
    switch (message.kind) {
        case "question":
            return <div className="message question">{message.text}</div>;
        case "answer":
            return message.answer.abstained
                ? <AbstentionCard answer={message.answer} />
                : <AnswerCard answer={message.answer} />;
        case "error":
            return <div className="message error">{message.text}</div>;
    }
}

export function MessageList({ messages, isWaiting }: MessageListProps) {
    const listEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        listEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [messages, isWaiting]);

    return (
        <div className="message-list" aria-live="polite">
            {messages.map((message, index) => (
                <MessageItem key={index} message={message} />
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
