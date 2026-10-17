import type { Citation } from "../types";

interface CitationBoxProps {
    citation: Citation;
}

function formatCitationLabel(citation: Citation) {
    const label = `${citation.document} ${citation.section}`;
    return citation.paragraph ? `${label} ${citation.paragraph}` : label;
}

export function CitationBox({ citation }: CitationBoxProps) {
    return (
        <details className="citation">
            <summary>
                <span className="citation-label">{formatCitationLabel(citation)}</span>
                {citation.title && <span className="citation-title">{citation.title}</span>}
            </summary>
            <p className="citation-text">{citation.text}</p>
        </details>
    );
}
