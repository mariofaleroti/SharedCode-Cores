from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..app_config import GuiAppConfig
from ..dependencies import require_customtkinter
from ..styles.colors import get_surface_colors
from ..styles.fonts import FontConfig
from ..widgets.form_controls import get_button_style_options, apply_standard_control_colors


DIALOG_KINDS = {"info", "success", "warning", "error", "question"}


@dataclass(frozen=True)
class DialogButton:
    """Declarative button used by GuiCore dialogs."""

    text: str
    result: str | bool | None = None
    style: str = "primary"
    closes_dialog: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "result": self.result,
            "style": self.style,
            "closes_dialog": self.closes_dialog,
        }


@dataclass(frozen=True)
class DialogSpec:
    """Visual contract for a generic GuiCore dialog.

    Dialogs stay generic: title, text, optional details and buttons. Project-specific
    copy and business decisions stay in each tool.
    """

    title: str
    message: str
    kind: str = "info"
    details: str = ""
    width: int = 520
    height: int = 280
    buttons: tuple[DialogButton, ...] = (DialogButton("Aceptar", True),)

    def normalized_kind(self) -> str:
        return normalize_dialog_kind(self.kind)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "message": self.message,
            "kind": self.normalized_kind(),
            "details": self.details,
            "width": self.width,
            "height": self.height,
            "buttons": [button.to_dict() for button in self.buttons],
        }


def normalize_dialog_kind(kind: str | None) -> str:
    normalized = (kind or "info").strip().lower()
    if normalized in DIALOG_KINDS:
        return normalized
    return "info"


def build_about_message(app_config: GuiAppConfig) -> str:
    version = f"\nVersión: {app_config.app_version}" if app_config.app_version else ""
    subtitle = f"\n{app_config.app_subtitle}" if app_config.app_subtitle else ""
    extra = f"\n\n{app_config.about_text}" if getattr(app_config, "about_text", "") else ""
    return (
        f"{app_config.app_name}{version}{subtitle}\n\n"
        "Interfaz construida sobre GuiCore.\n"
        "La lógica de cada herramienta se mantiene separada de la base visual compartida."
        f"{extra}"
    )


def build_help_message(app_config: GuiAppConfig) -> str:
    custom_help = getattr(app_config, "help_text", "")
    if custom_help:
        return custom_help
    return (
        f"{app_config.app_name} usa una interfaz base compartida del ecosistema.\n\n"
        "Panel izquierdo: controles y menú de la herramienta.\n"
        "Panel principal: contenido, resultados, progreso y acciones.\n\n"
        "Cada proyecto puede reemplazar estos textos por su propia ayuda específica."
    )


def _center_on_parent(dialog: Any, parent: Any, width: int, height: int) -> None:
    try:
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        dialog.geometry(f"{width}x{height}+{max(x, 0)}+{max(y, 0)}")
    except Exception:
        dialog.geometry(f"{width}x{height}")


def _safe_focus(widget: Any) -> None:
    try:
        widget.focus_set()
    except Exception:
        pass


def _build_dialog_shell(parent: Any, spec: DialogSpec, font_config: FontConfig | None = None, color_theme: str | None = None, surface_theme: str | None = None, appearance_mode: str | None = None) -> tuple[Any, Any, FontConfig]:
    ctk = require_customtkinter()
    fonts = font_config or FontConfig()
    surface = get_surface_colors(appearance_mode, surface_theme)
    dialog = ctk.CTkToplevel(parent)
    dialog.configure(fg_color=surface["root"])
    dialog.title(spec.title)
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)
    _center_on_parent(dialog, parent, spec.width, spec.height)

    frame = ctk.CTkFrame(dialog, corner_radius=14, fg_color=surface["card"])
    frame.pack(fill="both", expand=True, padx=18, pady=18)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1)

    title_label = ctk.CTkLabel(frame, text=spec.title, font=fonts.tuple("section", "bold"), anchor="w")
    title_label.grid(row=0, column=0, padx=16, pady=(16, 6), sticky="ew")

    return dialog, frame, fonts


def _add_message_body(frame: Any, spec: DialogSpec, fonts: FontConfig, surface_theme: str | None = None, appearance_mode: str | None = None) -> None:
    ctk = require_customtkinter()
    surface = get_surface_colors(appearance_mode, surface_theme)
    body_frame = ctk.CTkFrame(frame, fg_color="transparent")
    body_frame.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="nsew")
    body_frame.grid_columnconfigure(0, weight=1)
    body_frame.grid_rowconfigure(0, weight=0)
    if spec.details:
        body_frame.grid_rowconfigure(1, weight=1)

    message_label = ctk.CTkLabel(
        body_frame,
        text=spec.message,
        font=fonts.tuple("body"),
        text_color=surface["border"],
        justify="left",
        anchor="nw",
        wraplength=spec.width - 90,
    )
    message_label.grid(row=0, column=0, sticky="ew")

    if spec.details:
        details_box = ctk.CTkTextbox(body_frame, font=fonts.tuple("small"), wrap="word", height=90, fg_color=surface["card_alt"], border_color=surface["border"], border_width=1)
        details_box.grid(row=1, column=0, pady=(10, 0), sticky="nsew")
        details_box.insert("1.0", spec.details)
        details_box.configure(state="disabled")


def _add_button_row(
    dialog: Any,
    frame: Any,
    spec: DialogSpec,
    fonts: FontConfig,
    set_result: Callable[[str | bool | None], None] | None = None,
    color_theme: str | None = None,
    surface_theme: str | None = None,
    appearance_mode: str | None = None,
) -> None:
    ctk = require_customtkinter()
    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="e")

    for index, button_spec in enumerate(spec.buttons):
        def command(current_button: DialogButton = button_spec) -> None:
            if set_result is not None:
                set_result(current_button.result)
            if current_button.closes_dialog:
                dialog.destroy()

        style_options = get_button_style_options(button_spec.style, color_theme, surface_theme, appearance_mode)
        button = ctk.CTkButton(button_frame, text=button_spec.text, command=command, font=fonts.tuple("body"), **style_options)
        button.grid(row=0, column=index, padx=(8 if index else 0, 0), pady=0, sticky="e")
        if index == len(spec.buttons) - 1:
            _safe_focus(button)


def show_dialog(parent: Any, spec: DialogSpec, font_config: FontConfig | None = None, color_theme: str | None = None, surface_theme: str | None = None, appearance_mode: str | None = None) -> Any:
    """Show a generic non-blocking modal dialog and return its CTkToplevel."""

    dialog, frame, fonts = _build_dialog_shell(parent, spec, font_config, color_theme, surface_theme, appearance_mode)
    _add_message_body(frame, spec, fonts, surface_theme, appearance_mode)
    _add_button_row(dialog, frame, spec, fonts, color_theme=color_theme, surface_theme=surface_theme, appearance_mode=appearance_mode)
    return dialog


def show_message_dialog(
    parent: Any,
    title: str,
    message: str,
    button_text: str = "Aceptar",
    font_config: FontConfig | None = None,
    width: int = 460,
    height: int = 240,
    kind: str = "info",
    details: str = "",
    color_theme: str | None = None,
    surface_theme: str | None = None,
    appearance_mode: str | None = None,
) -> Any:
    """Show a simple modal CustomTkinter message dialog.

    Kept compatible with the original GuiCore v0.1 helper while adding kind/details.
    """

    spec = DialogSpec(
        title=title,
        message=message,
        kind=kind,
        details=details,
        width=width,
        height=height,
        buttons=(DialogButton(button_text, True),),
    )
    return show_dialog(parent, spec, font_config, color_theme=color_theme, surface_theme=surface_theme, appearance_mode=appearance_mode)


def show_info_dialog(parent: Any, title: str, message: str, font_config: FontConfig | None = None, details: str = "", color_theme: str | None = None, surface_theme: str | None = None, appearance_mode: str | None = None) -> Any:
    return show_message_dialog(parent, title, message, font_config=font_config, kind="info", details=details, color_theme=color_theme, surface_theme=surface_theme, appearance_mode=appearance_mode)


def show_warning_dialog(parent: Any, title: str, message: str, font_config: FontConfig | None = None, details: str = "", color_theme: str | None = None, surface_theme: str | None = None, appearance_mode: str | None = None) -> Any:
    return show_message_dialog(parent, title, message, font_config=font_config, kind="warning", details=details, color_theme=color_theme, surface_theme=surface_theme, appearance_mode=appearance_mode)


def show_error_dialog(parent: Any, title: str, message: str, font_config: FontConfig | None = None, details: str = "", color_theme: str | None = None, surface_theme: str | None = None, appearance_mode: str | None = None) -> Any:
    height = 320 if details else 260
    return show_message_dialog(parent, title, message, font_config=font_config, kind="error", details=details, width=560, height=height, color_theme=color_theme, surface_theme=surface_theme, appearance_mode=appearance_mode)


def show_success_dialog(parent: Any, title: str, message: str, font_config: FontConfig | None = None, details: str = "", color_theme: str | None = None, surface_theme: str | None = None, appearance_mode: str | None = None) -> Any:
    return show_message_dialog(parent, title, message, font_config=font_config, kind="success", details=details, color_theme=color_theme, surface_theme=surface_theme, appearance_mode=appearance_mode)


def show_confirm_dialog(
    parent: Any,
    title: str,
    message: str,
    confirm_text: str = "Aceptar",
    cancel_text: str = "Cancelar",
    font_config: FontConfig | None = None,
    width: int = 500,
    height: int = 260,
    kind: str = "question",
    details: str = "",
    color_theme: str | None = None,
    surface_theme: str | None = None,
    appearance_mode: str | None = None,
) -> bool:
    """Show a blocking confirmation dialog and return True/False."""

    result = {"value": False}

    def set_result(value: str | bool | None) -> None:
        result["value"] = bool(value)

    spec = DialogSpec(
        title=title,
        message=message,
        kind=kind,
        details=details,
        width=width,
        height=height,
        buttons=(DialogButton(cancel_text, False, "secondary"), DialogButton(confirm_text, True, "primary")),
    )
    dialog, frame, fonts = _build_dialog_shell(parent, spec, font_config, color_theme, surface_theme, appearance_mode)
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    _add_message_body(frame, spec, fonts, surface_theme, appearance_mode)
    _add_button_row(dialog, frame, spec, fonts, set_result, color_theme=color_theme, surface_theme=surface_theme, appearance_mode=appearance_mode)
    parent.wait_window(dialog)
    return bool(result["value"])


def show_text_input_dialog(
    parent: Any,
    title: str,
    message: str,
    initial_value: str = "",
    placeholder: str = "",
    confirm_text: str = "Aceptar",
    cancel_text: str = "Cancelar",
    font_config: FontConfig | None = None,
    width: int = 520,
    height: int = 300,
    required: bool = False,
    color_theme: str | None = None,
    surface_theme: str | None = None,
    appearance_mode: str | None = None,
) -> str | None:
    """Show a blocking single-line input dialog.

    Returns the entered text, or None if cancelled/closed. When required=True, an
    empty confirmation keeps the dialog open and shows a small validation message.
    """

    ctk = require_customtkinter()
    result: dict[str, str | None] = {"value": None}
    spec = DialogSpec(title=title, message=message, kind="question", width=width, height=height)
    dialog, frame, fonts = _build_dialog_shell(parent, spec, font_config, color_theme, surface_theme, appearance_mode)
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    surface = get_surface_colors(appearance_mode, surface_theme)

    body_frame = ctk.CTkFrame(frame, fg_color="transparent")
    body_frame.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="nsew")
    body_frame.grid_columnconfigure(0, weight=1)

    message_label = ctk.CTkLabel(
        body_frame,
        text=message,
        font=fonts.tuple("body"),
        text_color=surface["border"],
        justify="left",
        anchor="w",
        wraplength=width - 90,
    )
    message_label.grid(row=0, column=0, sticky="ew")

    entry = ctk.CTkEntry(body_frame, placeholder_text=placeholder, font=fonts.tuple("body"))
    apply_standard_control_colors(entry, appearance_mode, surface_theme)
    entry.grid(row=1, column=0, pady=(12, 6), sticky="ew")
    if initial_value:
        entry.insert(0, initial_value)

    validation_label = ctk.CTkLabel(body_frame, text="", font=fonts.tuple("small"), text_color=surface["border"], anchor="w")
    validation_label.grid(row=2, column=0, sticky="ew")

    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="e")

    def cancel() -> None:
        result["value"] = None
        dialog.destroy()

    def accept() -> None:
        value = entry.get().strip()
        if required and not value:
            validation_label.configure(text="Este campo es obligatorio.")
            _safe_focus(entry)
            return
        result["value"] = value
        dialog.destroy()

    cancel_button = ctk.CTkButton(button_frame, text=cancel_text, command=cancel, font=fonts.tuple("body"), **get_button_style_options("secondary", color_theme, surface_theme, appearance_mode))
    cancel_button.grid(row=0, column=0, padx=(0, 8), sticky="e")
    accept_button = ctk.CTkButton(button_frame, text=confirm_text, command=accept, font=fonts.tuple("body"), **get_button_style_options("primary", color_theme, surface_theme, appearance_mode))
    accept_button.grid(row=0, column=1, sticky="e")

    entry.bind("<Return>", lambda _event: accept())
    entry.bind("<Escape>", lambda _event: cancel())
    _safe_focus(entry)

    parent.wait_window(dialog)
    return result["value"]


def show_about_dialog(parent: Any, app_config: GuiAppConfig, font_config: FontConfig | None = None, color_theme: str | None = None, surface_theme: str | None = None, appearance_mode: str | None = None) -> Any:
    return show_message_dialog(parent, "Acerca de", build_about_message(app_config), font_config=font_config, width=540, height=300, color_theme=color_theme, surface_theme=surface_theme, appearance_mode=appearance_mode)


def show_help_dialog(parent: Any, app_config: GuiAppConfig, font_config: FontConfig | None = None, color_theme: str | None = None, surface_theme: str | None = None, appearance_mode: str | None = None) -> Any:
    return show_message_dialog(parent, "Ayuda", build_help_message(app_config), font_config=font_config, width=560, height=320, color_theme=color_theme, surface_theme=surface_theme, appearance_mode=appearance_mode)
