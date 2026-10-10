import { ABSTENTION_NOTICE, ABSTENTION_REFERRAL, RELATED_CITATIONS_HEADING } from "../constants";
import type { Answer } from "../types";
import { CitationBox } from "./CitationBox";
import { AlertIcon } from "./icons";

interface AbstentionCardProps {
    answer: Answer;
}

export function AbstentionCard({ answer }: AbstentionCardProps) {
    return (
        <article className="message abstention">
            <div className="abstention-header">
                <AlertIcon />
                <div>
                    <p className="abstention-notice">{ABSTENTION_NOTICE}</p>
                    <p className="abstention-referral">{ABSTENTION_REFERRAL}</p>
                </div>
            </div>
            {answer.citations.length > 0 && (
                <div className="citations">
                    <p className="related-heading">{RELATED_CITATIONS_HEADING}</p>
                    {answer.citations.map((citation, index) => (
                        <CitationBox key={index} citation={citation} />
                    ))}
                </div>
            )}
        </article>
    );
}
