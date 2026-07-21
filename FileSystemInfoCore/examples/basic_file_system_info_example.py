from pathlib import Path
from file_system_info_core import get_directory_summary, get_path_info

path_info = get_path_info(Path("README.md"))
print(path_info.to_dict())

summary = get_directory_summary(Path("."))
print(summary.to_dict())
