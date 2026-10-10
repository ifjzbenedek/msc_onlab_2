import { EXAMPLE_QUESTIONS, EXAMPLES_LABEL, INTRO_TEXT, WELCOME_TITLE } from "../constants";

interface WelcomePanelProps {
    onAsk: (question: string) => void;
}

export function WelcomePanel({ onAsk }: WelcomePanelProps) {
    return (
        <section className="welcome">
            <h2>{WELCOME_TITLE}</h2>
            <p className="welcome-intro">{INTRO_TEXT}</p>
            <p className="welcome-label">{EXAMPLES_LABEL}</p>
            <ul className="example-list">
                {EXAMPLE_QUESTIONS.map((question) => (
                    <li key={question}>
                        <button type="button" className="example-question" onClick={() => onAsk(question)}>
                            {question}
                        </button>
                    </li>
                ))}
            </ul>
        </section>
    );
}
