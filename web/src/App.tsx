import { useState } from "react";

import { fetchAnswer } from "./api";
import { MessageList } from "./components/MessageList";
import { QuestionForm } from "./components/QuestionForm";
import { WelcomePanel } from "./components/WelcomePanel";
import { BRAND_MARK, DISCLAIMER_TEXT, ERROR_MESSAGE, PAGE_SUBTITLE, PAGE_TITLE } from "./constants";
import type { ChatMessage } from "./types";

export function App() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isWaiting, setIsWaiting] = useState(false);

    function addMessage(message: ChatMessage) {
        setMessages((previousMessages) => [...previousMessages, message]);
    }

    async function askQuestion(question: string) {
        addMessage({ kind: "question", text: question });
        setIsWaiting(true);
        try {
            addMessage({ kind: "answer", answer: await fetchAnswer(question) });
        } catch (error) {
            console.error(error);
            addMessage({ kind: "error", text: ERROR_MESSAGE });
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
            <main className="chat">
                {messages.length === 0
                    ? <WelcomePanel onAsk={askQuestion} />
                    : <MessageList messages={messages} isWaiting={isWaiting} />}
            </main>
            <footer className="composer">
                <QuestionForm onAsk={askQuestion} isWaiting={isWaiting} />
                <p className="disclaimer">{DISCLAIMER_TEXT}</p>
            </footer>
        </div>
    );
}
