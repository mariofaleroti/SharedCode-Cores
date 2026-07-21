from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = DOCS / "shared_code_map.md"

CORE_ORDER = [
    "AppCore",
    "CliCore",
    "ConfigCore",
    "FileScanCore",
    "DateTimeCore",
    "FileSystemInfoCore",
    "GuiCore",
    "JsonContractCore",
    "LoggingCore",
    "ProcessRunnerCore",
    "PlatformCore",
    "ReleaseCore",
    "ToolRuntimeCore",
]

DEFAULT_CORE_METADATA = {
    "AppCore": (
        "Identidad, metadatos y datos generales de cada herramienta externa.",
        "Base inicial funcional",
    ),
    "CliCore": (
        "Argumentos, flags, códigos de salida y comportamiento común de consola.",
        "Base inicial funcional",
    ),
    "ConfigCore": (
        "Carga, creación y validación de configuraciones JSON.",
        "Base inicial funcional",
    ),
    "FileScanCore": (
        "Escaneo seguro de carpetas y archivos.",
        "Base inicial funcional",
    ),
    "DateTimeCore": (
        "Fechas, horas, timestamps UTC/locales y conversión desde epoch seconds con formato estándar.",
        "Base inicial funcional",
    ),
    "FileSystemInfoCore": (
        "Metadata, tamaños, fechas y errores de filesystem.",
        "Base inicial funcional",
    ),
    "GuiCore": (
        "Componentes visuales reutilizables para herramientas con GUI e iconos centralizados Windows/Linux.",
        "Base visual estable con iconos heredables",
    ),
    "JsonContractCore": (
        "Creación, validación y análisis de contratos JSON estándar.",
        "Base inicial funcional",
    ),
    "LoggingCore": (
        "Logs estándar en consola y archivo.",
        "Base inicial funcional",
    ),
    "ProcessRunnerCore": (
        "Ejecución controlada de comandos externos.",
        "Base inicial funcional",
    ),
    "PlatformCore": (
        "Capa Windows/Linux para rutas, apertura de archivos/carpetas, detección de plataforma y detalles de filesystem.",
        "Base inicial portable Windows/Linux",
    ),
    "ReleaseCore": (
        "Ayudas para estructura de release, manifest y validaciones de empaquetado.",
        "Base inicial funcional",
    ),
    "ToolRuntimeCore": (
        "Rutas runtime/output/logs/temp de herramienta; se complementa con PlatformCore para rutas nativas por sistema.",
        "Base inicial funcional",
    ),
}


def extract_section(text, title):
    pattern = rf"## {re.escape(title)}\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, re.S)
    if not match:
        return ""
    return match.group(1).strip()


def first_paragraph(text):
    clean = text.strip()
    if not clean:
        return ""
    return clean.split("\n\n")[0].replace("\n", " ").strip()


def get_core_metadata(core_name: str, readme_text: str) -> tuple[str, str]:
    default_summary, default_status = DEFAULT_CORE_METADATA.get(core_name, ("Sin descripción.", "Sin descripción."))
    summary = first_paragraph(extract_section(readme_text, "Resumen")) or default_summary
    status = first_paragraph(extract_section(readme_text, "Estado actual")) or default_status
    return summary, status


def main():
    DOCS.mkdir(parents=True, exist_ok=True)

    lines = [
        "# SharedCode Map",
        "",
        "Mapa generado automáticamente desde los `README.md` de cada Core.",
        "",
        "```text",
        "SharedCode",
    ]

    details = []

    for core_name in CORE_ORDER:
        readme = ROOT / core_name / "README.md"
        if not readme.exists():
            resumen, estado = DEFAULT_CORE_METADATA.get(core_name, ("README.md no encontrado", "Sin descripción."))
        else:
            text = readme.read_text(encoding="utf-8")
            resumen, estado = get_core_metadata(core_name, text)

        lines.append(f"├─ {core_name}")
        lines.append(f"│  └─ {resumen}")
        details.append((core_name, resumen, estado))

    lines.append("```")
    lines.append("")
    lines.append("## Inventario")
    lines.append("")
    lines.append("| Core | Estado | Resumen |")
    lines.append("|---|---|---|")

    for core_name, resumen, estado in details:
        lines.append(f"| `{core_name}` | {estado} | {resumen} |")

    lines.append("")
    lines.append("## Regla de arquitectura")
    lines.append("")
    lines.append("```text")
    lines.append("SharedCode se usa en desarrollo.")
    lines.append("Cada herramienta empaqueta lo que necesita.")
    lines.append("Toolkit no depende de SharedCode.")
    lines.append("Toolkit consume releases estables por manifest.")
    lines.append("```")

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Mapa generado: {OUTPUT}")


if __name__ == "__main__":
    main()
