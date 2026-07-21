from sharedcode_meta import __version__

from .api import create_default_registry, render_many, render_report, render_report_data
from .contracts import build_report_document, load_report_json, validate_report_contract
from .validation import ContractValidationResult, validate_contract
from .exceptions import ContractValidationError, RenderCoreError, TemplateResolutionError, UnsupportedFormatError
from .options import RenderOptions
from .result import RenderResult

__all__ = [
    "__version__",
    "ContractValidationError",
    "RenderCoreError",
    "RenderOptions",
    "RenderResult",
    "TemplateResolutionError",
    "UnsupportedFormatError",
    "build_report_document",
    "create_default_registry",
    "load_report_json",
    "render_many",
    "render_report",
    "render_report_data",
    "validate_report_contract",
    "validate_contract",
    "ContractValidationResult",
]

