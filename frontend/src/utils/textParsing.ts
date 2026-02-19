
/**
 * Parses a string that might be a JSON object or just a plain string.
 * returns a cleaner label and a boolean indicating if it was JSON.
 */
export function parseLabelOrJson(text: string): { label: string; isJson: boolean } {
    if (!text || typeof text !== 'string') {
        return { label: '', isJson: false };
    }

    const trimmed = text.trim();
    if (!trimmed.startsWith("{")) {
        return { label: trimmed, isJson: false };
    }

    try {
        const parsed = JSON.parse(trimmed);

        // Check for "content.text" array pattern (Complex JSON from user report)
        if (parsed.content && Array.isArray(parsed.content.text) && parsed.content.text.length > 0) {
            const primaryText = parsed.content.text.join(", ");
            const contextType = parsed.context?.type ? `(${parsed.context.type})` : "";
            return { label: `${primaryText} ${contextType}`.trim(), isJson: true };
        }

        // Try to find a meaningful label from common keys
        const candidates = [
            parsed.topic,
            parsed.category,
            parsed.mention_type,
            parsed.context,
            parsed.label,
            parsed.name
        ];

        // Find the first non-empty string candidate
        const validLabel = candidates.find(c => typeof c === 'string' && c.trim().length > 0);

        if (validLabel) {
            return { label: validLabel, isJson: true };
        }

        // If we have an object but no clear label, fallback to a generic identifier or the full text
        // But for the specific case of the user report, if it's that big JSON blob, 
        // we might want to try to extract *something* rather than showing the blob.
        // If keys contain "brand" and "sentiment", maybe construct a label?
        if (parsed.brand && parsed.sentiment) {
            return { label: `${parsed.brand} (${parsed.sentiment})`, isJson: true };
        }

        return { label: trimmed, isJson: false };
    } catch (e) {
        return { label: trimmed, isJson: false };
    }
}
