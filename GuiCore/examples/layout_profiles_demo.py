from __future__ import annotations

import argparse

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from gui_core import (
    GuiAppConfig,
    GuiAppWindow,
    ResultsTable,
    TableColumn,
    get_layout_profile,
    require_customtkinter,
)

ctk = require_customtkinter()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visual comparison for GuiCore 1.1 layout profiles.",
    )
    parser.add_argument(
        "--profile",
        choices=("compact", "standard", "comfortable"),
        default="standard",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile = get_layout_profile(args.profile)

    app = GuiAppWindow(
        GuiAppConfig(
            app_name="GuiCore Layout Demo",
            app_subtitle=f"Perfil {profile.name}",
            app_version="1.1.0.dev1",
            layout_profile=profile,
            maximize_on_start=False,
            width=1180,
            height=760,
        )
    )

    section = app.add_sidebar_section(
        "Configuración",
        "Todos los tamaños y espacios provienen del perfil seleccionado.",
    )
    section.add_labeled_entry("Nombre", value="ShadowBackup")
    section.add_labeled_combo(
        "Modo",
        ("Automático", "Manual", "Solo prueba"),
    )
    section.add_path_picker("Ruta", placeholder="Seleccionar carpeta...")
    section.add_switch("Automatización habilitada", default=True)
    section.add_action_button(
        "Ejecutar demostración",
        command=lambda: app.set_status(
            f"Perfil {profile.name} ejecutado correctamente."
        ),
    )

    summary = app.add_content_card(
        "Perfil activo",
        "La lógica es idéntica; solo cambia la densidad visual declarada.",
    )
    summary_label = ctk.CTkLabel(
        summary.content_frame,
        text=(
            f"{profile.name}: control={profile.control_height}px · "
            f"acción={profile.action_height}px · "
            f"separación={profile.widget_gap}px"
        ),
        font=app.font_config.tuple("body"),
        anchor="w",
    )
    summary_label.grid(row=0, column=0, sticky="ew")

    table_card = app.add_content_card(
        "Tokens de layout",
        "Valores serializables disponibles para cualquier herramienta.",
        row_weight=1,
    )
    table_card.frame.grid(sticky="nsew")
    table_card.content_frame.grid_rowconfigure(0, weight=1)

    table = ResultsTable(
        table_card.content_frame,
        columns=(
            TableColumn("token", "Token", width=260),
            TableColumn("value", "Valor", width=160),
        ),
        enable_sorting=False,
        enable_tooltips=False,
    )
    table.set_rows(
        {"token": key, "value": value}
        for key, value in profile.to_dict().items()
    )
    app.register_results_table(table)

    app.set_status(
        "Ejecutar con --profile compact, standard o comfortable para comparar."
    )
    app.mainloop()


if __name__ == "__main__":
    main()
