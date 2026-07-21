from __future__ import annotations

from typing import Dict

RESULTS_DENSITY_OPTIONS = [
    "Compacta",
    "Normal",
    "Cómoda",
]

RESULTS_DENSITY_ROW_HEIGHT: Dict[str, int] = {
    "Compacta": 21,
    "Normal": 24,
    "Cómoda": 30,
}


def get_results_density_row_height(density: str | None = "Normal") -> int:
    return RESULTS_DENSITY_ROW_HEIGHT.get(str(density or "Normal"), RESULTS_DENSITY_ROW_HEIGHT["Normal"])
