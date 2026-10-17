import { useState } from "react";

import { AskError, fetchAnswer } from "./api";
import { ConnectionBanner } from "./components/ConnectionBanner";
import { MessageList } from "./components/MessageList";
import { QuestionForm } from "./components/QuestionForm";
import { WelcomePanel } from "./components/WelcomePanel";
import {
    BRAND_MARK,
    DISCLAIMER_TEXT,
    INTERNAL_ERROR,
    PAGE_SUBTITLE,
    PAGE_TITLE,
    SERVER_UNREACHABLE_ERROR,
} from "./constants";
import { useBackendStatus } from "./hooks/useBackendStatus";
import type { ChatMessage } from "./types";

export function App() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isWaiting, setIsWaiting] = useState(false);
    const [isBackendReachable, setIsBackendReachable] = useBackendStatus();

    function addMessage(message: ChatMessage) {
        setMessages((previousMessages) => [...previousMessages, message]);
    }

    async function askQuestion(question: string) {
        addMessage({ kind: "question", text: question });
        setIsWaiting(true);
        try {
            addMessage({ kind: "answer", answer: await fetchAnswer(question) });
            setIsBackendReachable(true);
        } catch (error) {
            console.error(error);
            const code = error instanceof AskError ? error.code : INTERNAL_ERROR;
            addMessage({ kind: "error", code, question });
            if (code === SERVER_UNREACHABLE_ERROR) {
                setIsBackendReachable(false);
            }
        } finally {
            setIsWaiting(false);
        }
    }

    return (
        <div className="app">
            <header className="app-header">
                <div className="app-header-inner">
                    <span className="brand-mark" aria-hidden="true">{BRAND_MARK}</span>
                    <div>
                        <h1>{PAGE_TITLE}</h1>
                        <p className="app-subtitle">{PAGE_SUBTITLE}</p>
                    </div>
                </div>
            </header>
            {!isBackendReachable && <ConnectionBanner />}
            <main className="chat">
                {messages.length === 0
                    ? <WelcomePanel onAsk={askQuestion} />
                    : <MessageList messages={messages} isWaiting={isWaiting} onRetry={askQuestion} />}
            </main>
            <footer className="composer">
                <QuestionForm onAsk={askQuestion} isWaiting={isWaiting} />
                <p className="disclaimer">{DISCLAIMER_TEXT}</p>
            </footer>
        </div>
    );
}
