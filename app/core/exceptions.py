"""Domain exceptions used by the gateway."""


class GatewayError(Exception):
    """Base class for expected gateway failures."""


class ConfigurationError(GatewayError):
    """Raised when configuration cannot be loaded or validated."""


class AuthenticationError(GatewayError):
    """Raised when request authentication fails."""


class RequestValidationError(GatewayError):
    """Raised when gateway-level validation fails."""


class RoutingError(GatewayError):
    """Raised when no eligible model can be selected."""


class ModelUnavailableError(GatewayError):
    """Raised when a requested model is unavailable."""


class InferenceTimeoutError(GatewayError):
    """Raised when inference exceeds the configured timeout."""


class ProviderError(GatewayError):
    """Raised when a model provider returns an error."""

