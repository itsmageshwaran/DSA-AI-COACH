"""Context builder and token budget pruning utilities."""

from __future__ import annotations

import re


def estimate_token_count(text: str) -> int:
    """Estimate token count for a text string using character heuristic."""
    if not text:
        return 0
    # Average ~4 characters per token
    return max(1, len(text) // 4)


def prune_code_context(code: str, max_tokens: int = 500) -> str:
    """Prune code comments and truncate lines if code exceeds maximum token budget."""
    if estimate_token_count(code) <= max_tokens:
        return code

    # Strip multi-line docstrings and single line comments
    stripped = re.sub(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|#.*', "", code)

    lines = [line for line in stripped.splitlines() if line.strip()]
    pruned_lines: list[str] = []
    current_tokens = 0

    for line in lines:
        line_tokens = estimate_token_count(line)
        if current_tokens + line_tokens > max_tokens:
            pruned_lines.append("# ... [Code truncated to fit context token limit]")
            break
        pruned_lines.append(line)
        current_tokens += line_tokens

    return "\n".join(pruned_lines)
