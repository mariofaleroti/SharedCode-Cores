from pathlib import Path
from release_core import build_release_package

result = build_release_package(
    source_dir=Path("MyTool"),
    release_dir=Path("release/MyTool"),
)

print(result.to_dict())
