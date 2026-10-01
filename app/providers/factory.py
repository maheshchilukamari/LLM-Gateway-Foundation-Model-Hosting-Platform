"""Provider factory and registry."""

from app.providers.base import ModelProvider
from app.providers.huggingface import HuggingFaceProvider
from app.providers.mock import MockProvider


class ProviderFactory:
    """Resolve provider implementations by configured provider name."""

    def __init__(self, prefer_mock: bool = True) -> None:
        self._prefer_mock = prefer_mock
        self._mock = MockProvider()
        self._huggingface: HuggingFaceProvider | None = None

    def get_provider(self, provider: str) -> ModelProvider:
        if self._prefer_mock or provider == "mock":
            return self._mock
        if provider == "huggingface":
            if self._huggingface is None:
                self._huggingface = HuggingFaceProvider()
            return self._huggingface
        return self._mock

