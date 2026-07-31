from __future__ import annotations

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from gui_core import (
    GuiActionButton,
    GuiAppConfig,
    GuiAppWindow,
    GuiMenuItem,
    KeyValueItem,
    KeyValueTable,
    SidebarConfig,
)


def main() -> None:
    app = GuiAppWindow(
        GuiAppConfig(
            app_name="GuiCore Task Demo",
            app_subtitle="Operaciones seguras en segundo plano",
            app_version="1.1.0.dev6",
            layout_profile="compact",
            width=1080,
            height=700,
            maximize_on_start=False,
            sidebar_config=SidebarConfig(
                footer_label_visible=False,
                footer_columns=2,
                primary_action_columns=2,
            ),
            primary_actions=(
                GuiActionButton("Ejecutar", "run"),
                GuiActionButton(
                    "Cancelar",
                    "cancel",
                    style="secondary",
                    enabled=False,
                ),
            ),
            footer_items=(
                GuiMenuItem("Ayuda", "help"),
                GuiMenuItem("Salir", "exit"),
            ),
        )
    )

    card = app.add_content_card(
        "Estado de la operación",
        "El worker solo usa TaskContext; Tk se actualiza desde el hilo principal.",
        row_weight=1,
        sticky="nsew",
    )
    state = KeyValueTable(
        card.content_frame,
        (
            KeyValueItem("Estado", "Listo", "ready"),
            KeyValueItem("Hilo de interfaz", "Principal"),
            KeyValueItem("Progreso", "0%"),
        ),
        layout_profile="compact",
    )
    state.grid(row=0, column=0, sticky="nsew")
    app.register_visual_component(state)

    current_runner = {"value": None}

    def refresh_state(status, progress="0%"):
        semantic = "success" if status == "Completado" else "info"
        state.set_items(
            (
                KeyValueItem("Estado", status, semantic),
                KeyValueItem("Hilo de interfaz", "Principal"),
                KeyValueItem("Progreso", progress),
            )
        )

    def start_operation():
        def worker(context):
            for index in range(1, 101):
                context.report_progress(
                    index,
                    100,
                    message=f"Procesando paso {index} de 100",
                )
                context.sleep(0.025)
            return {"processed": 100}

        app.set_sidebar_action_enabled("run", False)
        app.set_sidebar_action_enabled("cancel", True)
        refresh_state("Ejecutando")

        runner = app.start_task(
            worker,
            task_key="demo",
            name="demo",
            start_message="Preparando operación...",
            success_message="Operación completada",
            disable_while_running=(app.get_sidebar_action_button("run"),),
            on_progress=lambda progress: refresh_state(
                "Ejecutando",
                f"{progress.percent}%",
            ),
            on_success=lambda _value: refresh_state("Completado", "100%"),
            on_cancelled=lambda _result: refresh_state("Cancelado"),
            on_finished=lambda _result: (
                app.set_sidebar_action_enabled("run", True),
                app.set_sidebar_action_enabled("cancel", False),
            ),
        )
        current_runner["value"] = runner

    def cancel_operation():
        runner = current_runner.get("value")
        if runner is not None:
            runner.cancel()

    app.set_sidebar_action("run", start_operation)
    app.set_sidebar_action("cancel", cancel_operation)
    app.set_status("Ejecutar inicia una tarea cancelable y no bloquea la GUI.")
    app.mainloop()


if __name__ == "__main__":
    main()
