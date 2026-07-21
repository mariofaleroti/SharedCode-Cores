from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .contracts import normalize_report_contract, validate_report_contract
from .exceptions import ContractValidationError


@dataclass(slots=True)
class ContractValidationResult:
    ok: bool
    data: dict[str, Any]
    source: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    diagnostics: list[dict[str, Any]] = field(default_factory=list)

    def raise_if_invalid(self) -> None:
        if not self.ok:
            message = "; ".join(self.errors) if self.errors else "Contract validation failed."
            raise ContractValidationError(message)


def validate_contract(
    report_data: dict[str, Any],
    *,
    contract_profile: str = "tool_report",
) -> ContractValidationResult:
    """Validate a report contract through JsonContractCore.

    RenderCore deliberately has no local, legacy or bypass validator. The shared
    JSON contract belongs to JsonContractCore. If JsonContractCore is missing or
    rejects the payload, RenderCore must not render.
    """

    bridge_result = _run_json_contract_core(
        report_data,
        contract_profile=contract_profile,
    )
    bridge_result.raise_if_invalid()

    # Defensive boundary only: do not fix the contract; just ensure the object
    # received from JsonContractCore still has the strict shape RenderCore needs.
    normalized = normalize_report_contract(bridge_result.data)
    bridge_result.data = normalized
    return bridge_result


def _run_json_contract_core(
    report_data: dict[str, Any],
    *,
    contract_profile: str,
) -> ContractValidationResult:
    import importlib

    import_candidates = [
        "json_contract_core",
        "JsonContractCore.json_contract_core",
        "SharedCode.JsonContractCore.json_contract_core",
    ]
    submodule_candidates = ["", ".api", ".contracts", ".validators", ".validation"]
    callable_candidates = [
        "validate_tool_report_contract",
        "validate_report_contract",
        "validate_json_contract",
        "validate_contract",
        "validate",
    ]

    import_errors: list[str] = []

    for package_name in import_candidates:
        for suffix in submodule_candidates:
            module_name = f"{package_name}{suffix}"
            try:
                module = importlib.import_module(module_name)
            except Exception as exc:
                import_errors.append(f"{module_name}: {exc}")
                continue

            for callable_name in callable_candidates:
                validator_fn = getattr(module, callable_name, None)
                if not callable(validator_fn):
                    continue

                source = f"{module_name}.{callable_name}"
                try:
                    raw_result = _call_json_contract_validator(
                        validator_fn,
                        report_data,
                        contract_profile=contract_profile,
                    )
                except Exception as exc:
                    raise ContractValidationError(f"JsonContractCore validator failed in {source}: {exc}") from exc

                return _coerce_json_contract_result(
                    raw_result,
                    fallback_data=report_data,
                    source=source,
                )

    details = " | ".join(import_errors[:5])
    suffix = f" Import attempts: {details}" if details else ""
    raise ContractValidationError(
        "JsonContractCore is required by RenderCore v0.8.0 and no compatible validator was found."
        + suffix
    )


def _call_json_contract_validator(
    validator_fn: Any,
    report_data: dict[str, Any],
    *,
    contract_profile: str,
) -> Any:
    """Call supported JsonContractCore signatures."""

    attempts = [
        lambda: validator_fn(report_data, strict=True, contract_profile=contract_profile),
        lambda: validator_fn(report_data, strict=True, profile=contract_profile),
        lambda: validator_fn(report_data, contract_profile=contract_profile),
        lambda: validator_fn(report_data, profile=contract_profile),
        lambda: validator_fn(report_data, strict=True),
        lambda: validator_fn(report_data, contract_profile),
        lambda: validator_fn(report_data),
    ]

    last_error: Exception | None = None
    for attempt in attempts:
        try:
            return attempt()
        except TypeError as exc:
            last_error = exc
            continue

    if last_error:
        raise last_error
    return validator_fn(report_data)


def _coerce_json_contract_result(
    raw_result: Any,
    *,
    fallback_data: dict[str, Any],
    source: str,
) -> ContractValidationResult:
    """Normalize common JsonContractCore return shapes without repairing data."""

    if raw_result is None:
        validate_report_contract(fallback_data)
        return ContractValidationResult(
            ok=True,
            data=fallback_data,
            source=source,
            diagnostics=[
                {
                    "level": "info",
                    "code": "json_contract_core_no_payload",
                    "message": "JsonContractCore returned no payload; original validated data was used.",
                }
            ],
        )

    if isinstance(raw_result, dict):
        ok = bool(raw_result.get("ok", raw_result.get("valid", True)))
        data = (
            raw_result.get("normalized_data")
            or raw_result.get("normalized")
            or raw_result.get("data")
            or raw_result.get("report_data")
            or fallback_data
        )
        warnings = _as_text_list(raw_result.get("warnings", []))
        errors = _as_text_list(raw_result.get("errors", []))
        diagnostics = _as_diagnostic_list(raw_result.get("diagnostics", []))

        if not isinstance(data, dict):
            return ContractValidationResult(
                ok=False,
                data=fallback_data,
                source=source,
                errors=["JsonContractCore returned a non-dictionary payload."],
                diagnostics=diagnostics,
            )

        if not ok:
            return ContractValidationResult(
                ok=False,
                data=data,
                source=source,
                warnings=warnings,
                errors=errors or ["JsonContractCore rejected the report contract."],
                diagnostics=diagnostics,
            )

        validate_report_contract(data)
        return ContractValidationResult(
            ok=True,
            data=data,
            source=source,
            warnings=warnings,
            errors=[],
            diagnostics=diagnostics,
        )

    ok_attr = getattr(raw_result, "ok", getattr(raw_result, "valid", True))
    data_attr = (
        getattr(raw_result, "normalized_data", None)
        or getattr(raw_result, "normalized", None)
        or getattr(raw_result, "data", None)
        or getattr(raw_result, "report_data", None)
        or fallback_data
    )
    warnings_attr = getattr(raw_result, "warnings", [])
    errors_attr = getattr(raw_result, "errors", [])
    diagnostics_attr = getattr(raw_result, "diagnostics", [])

    if not isinstance(data_attr, dict):
        return ContractValidationResult(
            ok=False,
            data=fallback_data,
            source=source,
            warnings=_as_text_list(warnings_attr),
            errors=["JsonContractCore returned a non-dictionary payload."],
            diagnostics=_as_diagnostic_list(diagnostics_attr),
        )

    if not bool(ok_attr):
        return ContractValidationResult(
            ok=False,
            data=data_attr,
            source=source,
            warnings=_as_text_list(warnings_attr),
            errors=_as_text_list(errors_attr) or ["JsonContractCore rejected the report contract."],
            diagnostics=_as_diagnostic_list(diagnostics_attr),
        )

    validate_report_contract(data_attr)
    return ContractValidationResult(
        ok=True,
        data=data_attr,
        source=source,
        warnings=_as_text_list(warnings_attr),
        errors=[],
        diagnostics=_as_diagnostic_list(diagnostics_attr),
    )


def _as_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return [str(value)]


def _as_diagnostic_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, list):
        diagnostics: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                diagnostics.append(item)
            else:
                diagnostics.append({"level": "info", "message": str(item)})
        return diagnostics
    if isinstance(value, dict):
        return [value]
    return [{"level": "info", "message": str(value)}]
