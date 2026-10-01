"""Responsible-AI extension hooks."""


class PiiRedactor:
    """Extension point for PII redaction. Disabled by default."""

    def redact(self, text: str) -> str:
        return text


class HumanReviewHook:
    """Extension point for human review workflows."""

    async def submit_if_required(self, request_id: str, text: str) -> None:
        del request_id, text

