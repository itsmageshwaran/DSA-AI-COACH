"""Input guardrail for prompt injection defense and PII redaction."""

from __future__ import annotations

import re

from src.infrastructure.ai.schemas import GuardrailValidationResult

INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?system\s+prompts?", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+dan", re.IGNORECASE),
    re.compile(r"forget\s+all\s+(rules|constraints)", re.IGNORECASE),
    re.compile(r"override\s+system\s+role", re.IGNORECASE),
]

PII_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b"), "[REDACTED_CREDIT_CARD]"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"), "[REDACTED_JWT]"),
]


class InputGuardrail:
    """Input safety validator defending against prompt injections and redacting sensitive PII."""

    def validate(self, prompt: str) -> GuardrailValidationResult:
        """Inspect prompt for safety violations and apply PII redaction filters."""
        flagged_reasons: list[str] = []
        is_safe = True
        risk_score = 0.0

        # 1. Prompt Injection Detection
        for pattern in INJECTION_PATTERNS:
            if pattern.search(prompt):
                is_safe = False
                flagged_reasons.append(f"Prompt Injection Pattern Detected: '{pattern.pattern}'")
                risk_score = 0.95
                break

        # 2. PII Sanitization
        sanitized_prompt = prompt
        for pii_regex, replacement in PII_PATTERNS:
            if pii_regex.search(sanitized_prompt):
                sanitized_prompt = pii_regex.sub(replacement, sanitized_prompt)

        return GuardrailValidationResult(
            is_safe=is_safe,
            flagged_reasons=flagged_reasons,
            sanitized_prompt=sanitized_prompt,
            risk_score=risk_score if not is_safe else 0.0,
        )


input_guardrail = InputGuardrail()
