from __future__ import annotations

import os
import subprocess
import sys
from typing import Any, Callable, Iterable, Mapping, Sequence

from ..app_config import GuiAppConfig
from ..dependencies import require_customtkinter
from ..dialogs import (
    show_about_dialog,
    show_confirm_dialog,
    show_error_dialog,
    show_help_dialog,
    show_info_dialog,
    show_message_dialog,
    show_success_dialog,
    show_text_input_dialog,
    show_warning_dialog,
)
from ..constants import DEFAULT_APPEARANCE_MODE, DEFAULT_COLOR_THEME
from ..preferences import GuiPreferences
from ..styles.colors import get_surface_colors
from ..styles.fonts import FontConfig
from ..theme import apply_runtime_theme, apply_theme
from ..windows import apply_window_icon, set_window_icon_metadata, show_settings_window
from ..widgets import ButtonRow, ContentPanel, ProgressPanel, ResultsTable, SectionCard, Sidebar, SidebarFormSection, StatusBar


def build_restart_arguments(
    executable: str | None = None,
    argv: Sequence[str] | None = None,
    frozen: bool | None = None,
) -> list[str]:
    """Return a safe argument vector to relaunch the current app.

    In normal Python execution the command is ``python <script> <args>``.
    In PyInstaller/frozen execution the command is ``<tool.exe> <args>``.
    """

    executable_path = executable or sys.executable
    current_argv = list(argv if argv is not None else sys.argv)
    is_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else bool(frozen)

    if not executable_path:
        raise RuntimeError("No executable path available to restart the application.")

    if is_frozen:
        return [executable_path, *current_argv[1:]]
    return [executable_path, *current_argv]


def restart_current_process() -> None:
    """Replace the current process with a fresh copy of the same app."""

    args = build_restart_arguments()
    try:
        os.execv(args[0], args)
    except OSError:
        # Fallback for environments where execv cannot replace the GUI process.
        subprocess.Popen(args, close_fds=True)
        os._exit(0)


class GuiAppWindow:
    """Reusable application shell for CustomTkinter tools.

    The class wraps a CTk root instead of subclassing it so importing GuiCore remains
    safe in environments where CustomTkinter is not installed.
    """

    def __init__(self, app_config: GuiAppConfig, font_config: FontConfig | None = None) -> None:
        self.app_config = app_config
        self.preferences = app_config.preferences.normalized()
        # Compatibility: tools created before GuiPreferences may still pass only
        # ThemeConfig through GuiAppConfig. Honor that when preferences are left
        # at their defaults.
        if (
            self.preferences.appearance_mode == DEFAULT_APPEARANCE_MODE
            and self.preferences.color_theme == DEFAULT_COLOR_THEME
            and (
                app_config.theme_config.appearance_mode != DEFAULT_APPEARANCE_MODE
                or app_config.theme_config.color_theme != DEFAULT_COLOR_THEME
            )
        ):
            self.preferences = GuiPreferences(
                appearance_mode=app_config.theme_config.appearance_mode,
                color_theme=app_config.theme_config.color_theme,
                font_family=self.preferences.font_family,
                font_size=self.preferences.font_size,
                table_density=self.preferences.table_density,
                surface_theme=self.preferences.surface_theme,
            ).normalized()
        if font_config is not None:
            self.preferences = GuiPreferences(
                appearance_mode=self.preferences.appearance_mode,
                color_theme=self.preferences.color_theme,
                font_family=font_config.family,
                font_size=font_config.size_option,
                table_density=self.preferences.table_density,
                surface_theme=self.preferences.surface_theme,
            ).normalized()
        self.font_config = self.preferences.to_font_config()
        # Runtime appearance is intentionally frozen after startup. Changing the
        # global CustomTkinter appearance while a complex app is already rendered
        # can freeze the window on some Windows environments. A new appearance
        # preference is kept as pending and should be applied on the next launch.
        self._runtime_appearance_mode = self.preferences.appearance_mode
        self.ctk = require_customtkinter()
        apply_theme(self.preferences.to_theme_config())
        self._results_tables: list[ResultsTable] = []
        self._visual_components: list[Any] = []
        self._preference_callbacks: list[Callable[[GuiPreferences], None]] = []
        self._restart_scheduled = False

        self.root = self.ctk.CTk()
        self._apply_root_surface()
        self.root.title(app_config.window_title)
        set_window_icon_metadata(self.root, app_config.icon_path, app_config.icon_png_path)
        self.window_icon_result = apply_window_icon(self.root, app_config.icon_path, app_config.icon_png_path)
        self.root.geometry(f"{app_config.width}x{app_config.height}")
        self.root.minsize(app_config.min_width, app_config.min_height)

        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self.root, app_config, self.font_config)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.content_panel = ContentPanel(self.root)
        self.content_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self._apply_component_visual_preferences(self.sidebar)
        self._apply_component_visual_preferences(self.content_panel)

        # Layout doctrine:
        #   row 0          -> primary/header content card
        #   row 1          -> active operation progress panel
        #   row 2..n       -> result/data content cards
        #   row 100        -> footer status bar
        # Progress belongs close to the data being generated; the footer is only
        # for the general application status.
        self._progress_row = 1
        self._status_row = 100

        self.progress_panel = ProgressPanel(self.content_panel.frame, self.font_config)
        self.progress_panel.apply_visual_preferences(self.font_config, self.preferences.color_theme, self.preferences.surface_theme, self._runtime_appearance_mode)
        self.progress_panel.grid(row=self._progress_row, column=0, padx=20, pady=(0, 12), sticky="ew")
        self.progress_panel.hide()

        self.status_bar = StatusBar(self.content_panel.frame, self.font_config)
        self.status_bar.grid(row=self._status_row, column=0, sticky="ew")
        self._apply_component_visual_preferences(self.status_bar)

        self._content_row = 0
        self._register_default_actions()

        if app_config.maximize_on_start:
            self.root.after(120, self.maximize_window)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.root, name)

    def _register_default_actions(self) -> None:
        self.sidebar.set_action("exit", self.root.destroy)
        self.sidebar.set_action("about", self.show_about)
        self.sidebar.set_action("help", self.show_help)
        self.sidebar.set_action("settings", self.show_settings)


    def _apply_root_surface(self) -> None:
        try:
            surface = get_surface_colors(self._runtime_appearance_mode, self.preferences.surface_theme)
            self.root.configure(fg_color=surface["root"])
        except Exception:
            pass

    def _apply_component_visual_preferences(self, component: Any) -> None:
        apply_method = getattr(component, "apply_visual_preferences", None)
        if not callable(apply_method):
            return
        try:
            apply_method(
                font_config=self.font_config,
                color_theme=self.preferences.color_theme,
                surface_theme=self.preferences.surface_theme,
                appearance_mode=self._runtime_appearance_mode,
            )
        except TypeError:
            try:
                apply_method(self.font_config, self.preferences.color_theme)
            except Exception:
                pass
        except Exception:
            pass

    def show_settings(self) -> Any:
        return show_settings_window(
            self.root,
            preferences=self.preferences,
            font_config=self.font_config,
            on_apply=self.apply_preferences,
        )

    def apply_preferences(self, preferences: GuiPreferences) -> None:
        requested_preferences = preferences.normalized()
        appearance_changed = requested_preferences.appearance_mode != self._runtime_appearance_mode

        self.preferences = requested_preferences
        self.font_config = self.preferences.to_font_config()
        # Deliberately do not call CustomTkinter appearance setters here. Live
        # theme switching can freeze the rendered window; appearance is applied
        # only during startup. Accent/base colors, font and density remain live-safe.
        apply_runtime_theme(self.preferences.to_theme_config())

        self._apply_root_surface()
        self._apply_component_visual_preferences(self.sidebar)
        self._apply_component_visual_preferences(self.content_panel)
        self._apply_component_visual_preferences(self.progress_panel)
        self._apply_component_visual_preferences(self.status_bar)

        for component in list(self._visual_components):
            self._apply_component_visual_preferences(component)

        for table in list(self._results_tables):
            try:
                table.apply_visual_preferences(
                    self.font_config,
                    self.preferences.table_density,
                    color_theme=self.preferences.color_theme,
                    surface_theme=self.preferences.surface_theme,
                    appearance_mode=self._runtime_appearance_mode,
                )
            except TypeError:
                table.apply_visual_preferences(self.font_config, self.preferences.table_density)
            except Exception:
                pass

        for callback in list(self._preference_callbacks):
            callback(self.preferences)

        if appearance_changed and self.app_config.restart_on_appearance_change:
            self.set_status(
                f"Tema cambiado a {self.preferences.appearance_label}. Reiniciando la aplicación para aplicar el tema..."
            )
            self.schedule_restart()
            return

        restart_note = " · requiere reiniciar" if appearance_changed else ""
        self.set_status(
            f"Configuración aplicada · tema={self.preferences.appearance_label}{restart_note} · acento={self.preferences.color_theme_label} · base={self.preferences.surface_theme_label} · fuente={self.preferences.font_family} · tabla={self.preferences.table_density}"
        )

    def schedule_restart(self, delay_ms: int | None = None) -> None:
        """Restart the current application after the current GUI callbacks finish."""

        if self._restart_scheduled:
            return
        self._restart_scheduled = True
        restart_delay = self.app_config.restart_delay_ms if delay_ms is None else max(0, int(delay_ms))
        self.root.after(restart_delay, self.restart_application)

    def restart_application(self) -> None:
        """Force a safe app restart.

        GuiCore uses this for appearance changes because rebuilding a large
        CustomTkinter interface in-place can freeze the rendered window on some
        Windows environments.
        """

        try:
            self.root.update_idletasks()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
        restart_current_process()

    def register_results_table(self, table: ResultsTable) -> ResultsTable:
        if table not in self._results_tables:
            self._results_tables.append(table)
            try:
                table.appearance_mode_provider = lambda: self._runtime_appearance_mode
                table.color_theme_provider = lambda: self.preferences.color_theme
                table.surface_theme_provider = lambda: self.preferences.surface_theme
            except Exception:
                pass
            table.apply_visual_preferences(
                self.font_config,
                self.preferences.table_density,
                color_theme=self.preferences.color_theme,
                surface_theme=self.preferences.surface_theme,
                appearance_mode=self._runtime_appearance_mode,
            )
        return table

    def register_visual_component(self, component: Any) -> Any:
        if component not in self._visual_components:
            self._visual_components.append(component)
            apply_method = getattr(component, "apply_visual_preferences", None)
            if callable(apply_method):
                self._apply_component_visual_preferences(component)
        return component

    def register_preferences_callback(self, callback: Callable[[GuiPreferences], None]) -> None:
        self._preference_callbacks.append(callback)

    def _dialog_visual_kwargs(self) -> dict[str, Any]:
        return {
            "color_theme": self.preferences.color_theme,
            "surface_theme": self.preferences.surface_theme,
            "appearance_mode": self._runtime_appearance_mode,
        }

    def show_about(self) -> Any:
        return show_about_dialog(self.root, self.app_config, self.font_config, **self._dialog_visual_kwargs())

    def show_help(self) -> Any:
        return show_help_dialog(self.root, self.app_config, self.font_config, **self._dialog_visual_kwargs())

    def show_message(self, title: str, message: str, kind: str = "info", details: str = "") -> Any:
        return show_message_dialog(self.root, title, message, font_config=self.font_config, kind=kind, details=details, **self._dialog_visual_kwargs())

    def show_info(self, title: str, message: str, details: str = "") -> Any:
        return show_info_dialog(self.root, title, message, font_config=self.font_config, details=details, **self._dialog_visual_kwargs())

    def show_success(self, title: str, message: str, details: str = "") -> Any:
        return show_success_dialog(self.root, title, message, font_config=self.font_config, details=details, **self._dialog_visual_kwargs())

    def show_warning(self, title: str, message: str, details: str = "") -> Any:
        return show_warning_dialog(self.root, title, message, font_config=self.font_config, details=details, **self._dialog_visual_kwargs())

    def show_error(self, title: str, message: str, details: str = "") -> Any:
        return show_error_dialog(self.root, title, message, font_config=self.font_config, details=details, **self._dialog_visual_kwargs())

    def confirm(self, title: str, message: str, confirm_text: str = "Aceptar", cancel_text: str = "Cancelar", details: str = "") -> bool:
        return show_confirm_dialog(
            self.root,
            title,
            message,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            font_config=self.font_config,
            details=details,
            **self._dialog_visual_kwargs(),
        )

    def ask_text(
        self,
        title: str,
        message: str,
        initial_value: str = "",
        placeholder: str = "",
        required: bool = False,
    ) -> str | None:
        return show_text_input_dialog(
            self.root,
            title,
            message,
            initial_value=initial_value,
            placeholder=placeholder,
            font_config=self.font_config,
            required=required,
            **self._dialog_visual_kwargs(),
        )

    def maximize_window(self) -> None:
        try:
            self.root.state("zoomed")
            return
        except Exception:
            pass
        try:
            self.root.attributes("-zoomed", True)
        except Exception:
            pass

    def mainloop(self) -> None:
        self.root.mainloop()

    def destroy(self) -> None:
        self.root.destroy()

    def set_sidebar_action(self, key: str, callback: Callable[[], None]) -> None:
        self.sidebar.set_action(key, callback)

    def add_sidebar_widget(self, widget: Any, **grid_options: Any) -> None:
        row = len(self.sidebar.controls_frame.winfo_children())
        options = {"row": row, "column": 0, "pady": (0, 10), "sticky": "ew"}
        options.update(grid_options)
        widget.grid(**options)

    def add_sidebar_section(self, title: str, subtitle: str = "") -> SidebarFormSection:
        section = SidebarFormSection(self.sidebar.controls_frame, title, subtitle, self.font_config)
        self.add_sidebar_widget(section)
        self.register_visual_component(section)
        return section

    def _get_content_grid_row(self, logical_row: int) -> int:
        """Return the physical grid row for user content.

        The first content card stays at the top. The progress panel owns the row
        immediately below it, so every additional content card is placed after
        the progress area. This keeps active progress above result tables without
        forcing each app to manage row numbers manually.
        """
        if logical_row == 0:
            return 0
        return logical_row + 1

    def add_content_card(self, title: str, subtitle: str = "", row_weight: int = 0) -> SectionCard:
        card = SectionCard(self.content_panel.frame, title, subtitle, self.font_config)
        grid_row = self._get_content_grid_row(self._content_row)
        card.grid(row=grid_row, column=0, padx=20, pady=(20 if self._content_row == 0 else 0, 12), sticky="ew")
        if row_weight:
            self.content_panel.frame.grid_rowconfigure(grid_row, weight=row_weight)
        self._content_row += 1
        self.register_visual_component(card)
        return card

    def clear_content(self) -> None:
        for child in list(self.content_panel.frame.winfo_children()):
            if child not in {self.progress_panel.frame, self.status_bar.frame}:
                child.destroy()
        self.hide_progress()
        self._content_row = 0

    def set_status(self, text: str) -> None:
        self.status_bar.set_text(text)

    def show_progress(self, message: str = "Preparando...", value: float = 0.0) -> None:
        self.progress_panel.show(message, value)

    def show_indeterminate_progress(self, message: str = "Procesando...") -> None:
        self.progress_panel.show_indeterminate(message)

    def update_progress(self, current: int | float, total: int | float, unit: str = "elementos", message: str | None = None) -> None:
        self.progress_panel.update(current, total, unit, message)

    def complete_progress(self, message: str = "Finalizado correctamente") -> None:
        self.progress_panel.complete(message)

    def hide_progress(self) -> None:
        self.progress_panel.hide()

    def create_button_row(
        self,
        parent: Any,
        buttons: Iterable[Mapping[str, Any]],
        commands: Mapping[str, Callable[[], None]],
    ) -> Any:
        return self.register_visual_component(ButtonRow(parent, buttons, commands=commands, font_config=self.font_config))


def create_gui_app_window(app_config: GuiAppConfig, font_config: FontConfig | None = None) -> GuiAppWindow:
    return GuiAppWindow(app_config, font_config)
