/**
 * Typewriter Text Component
 * 
 * Animated text that types out character by character
 */

import { useState, useEffect } from "react";

interface TypewriterTextProps {
    text: string;
    speed?: number;
    className?: string;
}

export function TypewriterText({ text, speed = 15, className = "" }: TypewriterTextProps) {
    const [displayText, setDisplayText] = useState("");

    useEffect(() => {
        let index = 0;
        setDisplayText("");
        const timer = setInterval(() => {
            if (index < text.length) {
                setDisplayText(prev => prev + text.charAt(index));
                index++;
            } else {
                clearInterval(timer);
            }
        }, speed);

        return () => clearInterval(timer);
    }, [text, speed]);

    return (
        <p className={`text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap ${className}`}>
            {displayText}
        </p>
    );
}
