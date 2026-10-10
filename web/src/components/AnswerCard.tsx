import { CITATIONS_HEADING, RELIABILITY_LABELS } from "../constants";
import type { Answer } from "../types";
import { CitationBox } from "./CitationBox";

interface AnswerCardProps {
    answer: Answer;
}

export function AnswerCard({ answer }: AnswerCardProps) {
    return (
        <article className="message answer">
            <p className="answer-text">{answer.text}</p>
            {answer.reliability && (
                <p className={`reliability ${answer.reliability}`}>{RELIABILITY_LABELS[answer.reliability]}</p>
            )}
            {answer.citations.length > 0 && (
                <div className="citations">
                    <p className="citations-heading">{CITATIONS_HEADING}</p>
                    {answer.citations.map((citation, index) => (
                        <CitationBox key={index} citation={citation} />
                    ))}
                </div>
            )}
        </article>
    );
}
