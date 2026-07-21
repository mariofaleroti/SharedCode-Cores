from __future__ import annotations

import sys
from pathlib import Path


def ensure_project_root_on_path() -> None:
    """Allow running examples directly from the examples folder.

    When Python runs ``examples/some_demo.py`` directly, it adds only
    ``examples`` to ``sys.path``. The project root must be added so the
    sibling package ``gui_core`` can be imported without installing it.
    """

    project_root = Path(__file__).resolve().parents[1]
    project_root_text = str(project_root)
    if project_root_text not in sys.path:
        sys.path.insert(0, project_root_text)
