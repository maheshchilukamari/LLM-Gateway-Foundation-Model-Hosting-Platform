"""Request and response policy enforcement."""

import re

from app.core.config import Settings, load_yaml_file
from app.core.exceptions import RequestValidationError


class PolicyEngine:
    """Apply configurable responsible-AI and technical validation policies."""

    def __init__(self, settings: Settings) -> None:
        self._config = load_yaml_file(settings.policies_config_path).get("policies", {})

    def validate_prompt(self, prompt: str) -> None:
        max_chars = self._config.get("request", {}).get("max_prompt_characters", 20_000)
        if len(prompt) > max_chars:
            raise RequestValidationError(f"Prompt exceeds max length of {max_chars} characters")

    def validate_response(self, response: str) -> None:
        if not response.strip():
            raise RequestValidationError("Provider returned an empty response")
        max_chars = self._config.get("response", {}).get("max_response_characters", 20_000)
        if len(response) > max_chars:
            raise RequestValidationError(f"Response exceeds max length of {max_chars} characters")
        for pattern in self._config.get("response", {}).get("blocked_patterns", []):
            if re.search(pattern, response):
                raise RequestValidationError("Response matched a blocked output policy")

