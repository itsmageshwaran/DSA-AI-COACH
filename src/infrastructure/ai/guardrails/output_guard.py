"""Output guardrail for code block extraction and JSON payload parsing."""

from __future__ import annotations

import json
import re
from typing import Any


class OutputGuardrail:
    """Output validator extracting code blocks, JSON payloads, and sanitizing output text."""

    def extract_code_blocks(self, text: str, language: str | None = None) -> list[str]:
        """Extract code block contents demarcated by markdown backticks."""
        pattern = r"```(?:" + (language or r"[a-zA-Z0-9+#]*") + r")?\n([\s\S]*?)```"
        matches = re.findall(pattern, text)
        return [m.strip() for m in matches]

    def extract_json_payload(self, text: str) -> dict[str, Any] | None:
        """Extract and parse structured JSON object from markdown text."""
        # Check direct JSON parse first
        try:
            val = json.loads(text)
            if isinstance(val, dict):
                return val
        except Exception:
            pass

        # Check markdown code block containing json
        json_blocks = self.extract_code_blocks(text, language="json")
        for block in json_blocks:
            try:
                val = json.loads(block)
                if isinstance(val, dict):
                    return val
            except Exception:
                continue

        # Regex search for first braced JSON substring
        match = re.search(r"(\{[\s\S]*\})", text)
        if match:
            try:
                val = json.loads(match.group(1))
                if isinstance(val, dict):
                    return val
            except Exception:
                pass

        return None


output_guardrail = OutputGuardrail()
