class RenderCoreError(Exception):
    """Base exception for RenderCore."""


class ContractValidationError(RenderCoreError):
    """Raised when the input JSON does not match the expected report contract."""


class UnsupportedFormatError(RenderCoreError):
    """Raised when a renderer format is not registered."""


class TemplateResolutionError(RenderCoreError):
    """Raised when an HTML template cannot be resolved."""
