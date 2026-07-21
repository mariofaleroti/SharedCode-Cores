from __future__ import annotations

from typing import Any

from .document import ReportTable


def extract_profile_tables(report_data: dict[str, Any]) -> list[ReportTable]:
    """Return profile-aware normalized tables for rendering/export.

    This is presentation normalization, not contract repair. The input must already
    be valid according to JsonContractCore and RenderCore's defensive boundary.
    """

    meta = report_data.get("meta", {}) if isinstance(report_data.get("meta"), dict) else {}
    profile = str(
        meta.get("report_type")
        or meta.get("config_type")
        or meta.get("file_type")
        or ""
    ).strip().lower()

    if profile == "disk_smart":
        return _extract_disk_smart_tables(report_data)

    return []


def _extract_disk_smart_tables(report_data: dict[str, Any]) -> list[ReportTable]:
    data = report_data.get("data", {}) if isinstance(report_data.get("data"), dict) else {}
    disks = data.get("disks", [])
    if not isinstance(disks, list):
        return []

    disk_rows: list[dict[str, Any]] = []
    ata_rows: list[dict[str, Any]] = []
    nvme_rows: list[dict[str, Any]] = []
    alternate_rows: list[dict[str, Any]] = []
    flagged_rows: list[dict[str, Any]] = []

    for index, disk in enumerate(disks, start=1):
        if not isinstance(disk, dict):
            continue

        life = disk.get("life") if isinstance(disk.get("life"), dict) else {}
        disk_key = f"disk_{index}"

        disk_rows.append(
            {
                "disk_index": index,
                "disk_key": disk_key,
                "smart_device": disk.get("smart_device"),
                "detected_type": disk.get("detected_type"),
                "storage_family": disk.get("storage_family"),
                "model": disk.get("model"),
                "serial": disk.get("serial"),
                "firmware": disk.get("firmware"),
                "evaluation_status": disk.get("evaluation_status"),
                "smart_global_passed": disk.get("smart_global_passed"),
                "smartctl_exit_code": disk.get("smartctl_exit_code"),
                "temperature_c": disk.get("temperature_c"),
                "power_on_hours": disk.get("power_on_hours"),
                "life_status": life.get("status"),
                "life_used_percent": life.get("used_percent"),
                "life_remaining_percent": life.get("remaining_percent"),
                "life_source": life.get("source"),
                "data_level": disk.get("data_level"),
                "deduplicated": disk.get("deduplicated"),
                "error": disk.get("error"),
            }
        )

        ata_attributes = disk.get("ata_attributes") if isinstance(disk.get("ata_attributes"), dict) else {}
        for attribute_key, attribute in ata_attributes.items():
            if not isinstance(attribute, dict):
                continue
            ata_rows.append(
                {
                    "disk_index": index,
                    "disk_key": disk_key,
                    "model": disk.get("model"),
                    "serial": disk.get("serial"),
                    "attribute_key": attribute_key,
                    "id": attribute.get("id"),
                    "name": attribute.get("name"),
                    "current": attribute.get("current"),
                    "worst": attribute.get("worst"),
                    "threshold": attribute.get("threshold"),
                    "raw": attribute.get("raw"),
                    "raw_text": attribute.get("raw_text"),
                }
            )

        nvme_health = disk.get("nvme_health") if isinstance(disk.get("nvme_health"), dict) else {}
        for metric, value in nvme_health.items():
            nvme_rows.append(
                {
                    "disk_index": index,
                    "disk_key": disk_key,
                    "model": disk.get("model"),
                    "serial": disk.get("serial"),
                    "metric": metric,
                    "value": value,
                }
            )

        alternate_devices = disk.get("alternate_smart_devices") if isinstance(disk.get("alternate_smart_devices"), list) else []
        for alternate_device in alternate_devices:
            alternate_rows.append(
                {
                    "disk_index": index,
                    "disk_key": disk_key,
                    "model": disk.get("model"),
                    "serial": disk.get("serial"),
                    "alternate_smart_device": alternate_device,
                }
            )

        flagged_items = disk.get("flagged_items") if isinstance(disk.get("flagged_items"), list) else []
        for item in flagged_items:
            flagged_rows.append(
                {
                    "disk_index": index,
                    "disk_key": disk_key,
                    "model": disk.get("model"),
                    "serial": disk.get("serial"),
                    "item": _scalar(item),
                }
            )

    tables: list[ReportTable] = []
    if disk_rows:
        tables.append(
            ReportTable(
                name="data_disks",
                title="Discos",
                columns=_collect_columns(disk_rows),
                rows=disk_rows,
                source_path="data.disks",
            )
        )
    if ata_rows:
        tables.append(
            ReportTable(
                name="data_ata_attributes",
                title="Atributos ATA",
                columns=_collect_columns(ata_rows),
                rows=ata_rows,
                source_path="data.disks[].ata_attributes",
            )
        )
    if nvme_rows:
        tables.append(
            ReportTable(
                name="data_nvme_health_metrics",
                title="Métricas NVMe",
                columns=_collect_columns(nvme_rows),
                rows=nvme_rows,
                source_path="data.disks[].nvme_health",
            )
        )
    if alternate_rows:
        tables.append(
            ReportTable(
                name="data_alternate_smart_devices",
                title="Dispositivos SMART alternativos",
                columns=_collect_columns(alternate_rows),
                rows=alternate_rows,
                source_path="data.disks[].alternate_smart_devices",
            )
        )
    if flagged_rows:
        tables.append(
            ReportTable(
                name="data_flagged_items",
                title="Elementos marcados",
                columns=_collect_columns(flagged_rows),
                rows=flagged_rows,
                source_path="data.disks[].flagged_items",
            )
        )

    return tables


def _collect_columns(rows: list[dict[str, Any]]) -> list[str]:
    columns: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in columns:
                columns.append(key)
    return columns


def _scalar(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)
