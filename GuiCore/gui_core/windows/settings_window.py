from __future__ import annotations

from typing import Any, Callable

from ..dependencies import require_customtkinter
from ..preferences import (
    APPEARANCE_LABEL_OPTIONS,
    COLOR_THEME_LABEL_OPTIONS,
    COLOR_THEME_LABEL_TO_VALUE,
    SURFACE_THEME_LABEL_OPTIONS,
    SURFACE_THEME_LABEL_TO_VALUE,
    GuiPreferences,
    normalize_appearance_label,
    normalize_color_theme_label,
    normalize_surface_theme_label,
)
from ..styles.colors import get_accent_colors, get_control_colors, get_surface_colors
from ..styles.fonts import APP_FONT_FAMILY_OPTIONS, APP_FONT_SIZE_OPTIONS, FontConfig
from ..styles.table_style import RESULTS_DENSITY_OPTIONS
from ..widgets.form_controls import ChoiceOption, LabeledComboBox
from ..visual_preferences import (
    VISUAL_PREFERENCES_ADVANCED,
    VISUAL_PREFERENCES_BASIC,
    VISUAL_PREFERENCES_NONE,
    normalize_visual_preferences_mode,
)
from .secondary_window import SecondaryWindow, SecondaryWindowConfig

PreferencesCallback = Callable[[GuiPreferences], None]


class SettingsWindow(SecondaryWindow):
    """Reusable visual settings window for GuiCore apps."""

    def __init__(
        self,
        parent: Any,
        preferences: GuiPreferences | None = None,
        font_config: FontConfig | None = None,
        on_apply: PreferencesCallback | None = None,
        preference_mode: str = VISUAL_PREFERENCES_ADVANCED,
    ) -> None:
        self.preferences = (preferences or GuiPreferences()).normalized()
        self.on_apply = on_apply
        self.preference_mode = normalize_visual_preferences_mode(preference_mode)
        if self.preference_mode == VISUAL_PREFERENCES_NONE:
            raise ValueError("The none preference mode does not create a settings window.")
        is_basic = self.preference_mode == VISUAL_PREFERENCES_BASIC
        super().__init__(
            parent,
            SecondaryWindowConfig(
                title="Configuración",
                subtitle=(
                    "Preferencias visuales esenciales."
                    if is_basic
                    else "Preferencias visuales avanzadas."
                ),
                width=680 if is_basic else 760,
                height=500 if is_basic else 540,
                min_width=640 if is_basic else 700,
                min_height=440 if is_basic else 470,
                modal=True,
                resizable=(False, False),
            ),
            font_config=font_config,
        )
        self._build_content()
        self.add_footer_button("Cancelar", self.close, style="secondary")
        self.add_footer_button("Aplicar", self.apply, style="ghost")
        self.add_footer_button("Aceptar", self.accept, style="primary")
        self.apply_visual_preferences(
            self.font_config,
            self.preferences.color_theme,
            self.preferences.surface_theme,
            self.preferences.appearance_mode,
        )

    def _build_content(self) -> None:
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.tabs = self.ctk.CTkTabview(self.content_frame)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=12, pady=10)

        visual_tab = self.tabs.add("Visual")
        visual_tab.grid_columnconfigure(0, weight=1)

        if self.preference_mode == VISUAL_PREFERENCES_BASIC:
            self._build_basic_visual_tab(visual_tab)
        else:
            general_tab = self.tabs.add("General")
            general_tab.grid_columnconfigure(0, weight=1)
            self._build_visual_tab(visual_tab)
            self._build_general_tab(general_tab)
        self.tabs.set("Visual")

    def _build_basic_visual_tab(self, parent: Any) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self.visual_scroll = self.ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
        )
        self.visual_scroll.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=6,
            pady=4,
        )
        self.visual_scroll.grid_columnconfigure(0, weight=1)

        self.typography_group = self.ctk.CTkFrame(
            self.visual_scroll,
            corner_radius=10,
        )
        self.typography_group.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=(0, 8),
        )
        self.typography_group.grid_columnconfigure((0, 1), weight=1, uniform="basic_visual")

        self.typography_title = self.ctk.CTkLabel(
            self.typography_group,
            text="Tema, fuente y densidad",
            font=self.font_config.tuple("section", "bold"),
            anchor="w",
        )
        self.typography_title.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=12,
            pady=(10, 6),
        )

        self.appearance_combo = LabeledComboBox(
            self.typography_group,
            "Tema (reinicia la app)",
            APPEARANCE_LABEL_OPTIONS,
            default_value=normalize_appearance_label(
                self.preferences.appearance_mode
            ),
            font_config=self.font_config,
        )
        self.appearance_combo.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=12,
            pady=(0, 8),
        )

        self.font_family_combo = LabeledComboBox(
            self.typography_group,
            "Fuente",
            APP_FONT_FAMILY_OPTIONS,
            default_value=self.preferences.font_family,
            font_config=self.font_config,
        )
        self.font_family_combo.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=(12, 6),
            pady=(0, 8),
        )

        self.font_size_combo = LabeledComboBox(
            self.typography_group,
            "Tamaño",
            APP_FONT_SIZE_OPTIONS,
            default_value=self.preferences.font_size,
            font_config=self.font_config,
        )
        self.font_size_combo.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=(6, 12),
            pady=(0, 8),
        )

        self.table_density_combo = LabeledComboBox(
            self.typography_group,
            "Densidad de tabla",
            RESULTS_DENSITY_OPTIONS,
            default_value=self.preferences.table_density,
            font_config=self.font_config,
        )
        self.table_density_combo.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=12,
            pady=(0, 10),
        )

    def _build_visual_tab(self, parent: Any) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self.visual_scroll = self.ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.visual_scroll.grid(row=0, column=0, sticky="nsew", padx=6, pady=4)
        self.visual_scroll.grid_columnconfigure(0, weight=1)

        self.palette_group = self.ctk.CTkFrame(self.visual_scroll, corner_radius=10)
        self.palette_group.grid(row=0, column=0, sticky="ew", padx=8, pady=(0, 8))
        self.palette_group.grid_columnconfigure((0, 1), weight=1, uniform="palette")

        self.palette_title = self.ctk.CTkLabel(
            self.palette_group,
            text="Tema y paleta",
            font=self.font_config.tuple("section", "bold"),
            anchor="w",
        )
        self.palette_title.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 5))

        self.appearance_combo = LabeledComboBox(
            self.palette_group,
            "Tema (reinicia la app)",
            APPEARANCE_LABEL_OPTIONS,
            default_value=normalize_appearance_label(self.preferences.appearance_mode),
            font_config=self.font_config,
        )
        self.appearance_combo.grid(row=1, column=0, sticky="ew", padx=(12, 6), pady=(0, 6))

        surface_options = [ChoiceOption(label=label, value=SURFACE_THEME_LABEL_TO_VALUE[label]) for label in SURFACE_THEME_LABEL_OPTIONS]
        self.surface_theme_combo = LabeledComboBox(
            self.palette_group,
            "Base de app",
            surface_options,
            default_value=normalize_surface_theme_label(self.preferences.surface_theme),
            font_config=self.font_config,
        )
        self.surface_theme_combo.grid(row=1, column=1, sticky="ew", padx=(6, 12), pady=(0, 6))

        accent_options = [ChoiceOption(label=label, value=COLOR_THEME_LABEL_TO_VALUE[label]) for label in COLOR_THEME_LABEL_OPTIONS]
        self.color_theme_combo = LabeledComboBox(
            self.palette_group,
            "Acento",
            accent_options,
            default_value=normalize_color_theme_label(self.preferences.color_theme),
            font_config=self.font_config,
        )
        self.color_theme_combo.grid(row=2, column=0, sticky="ew", padx=(12, 6), pady=(0, 6))

        self.typography_group = self.ctk.CTkFrame(self.visual_scroll, corner_radius=10)
        self.typography_group.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        self.typography_group.grid_columnconfigure(0, weight=2, uniform="typography")
        self.typography_group.grid_columnconfigure(1, weight=1, uniform="typography")
        self.typography_group.grid_columnconfigure(2, weight=1, uniform="typography")

        self.typography_title = self.ctk.CTkLabel(
            self.typography_group,
            text="Tipografía y tabla",
            font=self.font_config.tuple("section", "bold"),
            anchor="w",
        )
        self.typography_title.grid(row=0, column=0, columnspan=3, sticky="ew", padx=12, pady=(8, 5))

        self.font_family_combo = LabeledComboBox(
            self.typography_group,
            "Fuente",
            APP_FONT_FAMILY_OPTIONS,
            default_value=self.preferences.font_family,
            font_config=self.font_config,
        )
        self.font_family_combo.grid(row=1, column=0, sticky="ew", padx=(12, 6), pady=(0, 8))

        self.font_size_combo = LabeledComboBox(
            self.typography_group,
            "Tamaño",
            APP_FONT_SIZE_OPTIONS,
            default_value=self.preferences.font_size,
            font_config=self.font_config,
        )
        self.font_size_combo.grid(row=1, column=1, sticky="ew", padx=6, pady=(0, 8))

        self.table_density_combo = LabeledComboBox(
            self.typography_group,
            "Tabla",
            RESULTS_DENSITY_OPTIONS,
            default_value=self.preferences.table_density,
            font_config=self.font_config,
        )
        self.table_density_combo.grid(row=1, column=2, sticky="ew", padx=(6, 12), pady=(0, 8))

    def _build_general_tab(self, parent: Any) -> None:
        intro = self.ctk.CTkLabel(
            parent,
            text="Espacio reservado para configuraciones comunes futuras que no sean visuales.",
            font=self.font_config.tuple("body"),
            text_color="gray",
            anchor="w",
            justify="left",
            wraplength=560,
        )
        intro.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 12))

        examples = self.ctk.CTkLabel(
            parent,
            text=(
                "Ejemplos futuros:\n"
                "• Recordar tamaño y posición de ventana.\n"
                "• Confirmar antes de salir.\n"
                "• Preferencias de historial o comportamiento general.\n\n"
                "Cada herramienta seguirá pudiendo sumar sus propias secciones sin mezclar lógica de negocio en GuiCore."
            ),
            font=self.font_config.tuple("body"),
            text_color="gray",
            anchor="nw",
            justify="left",
            wraplength=560,
        )
        examples.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        super().apply_visual_preferences(font_config, color_theme, surface_theme, appearance_mode)
        if font_config is not None:
            self.font_config = font_config
        surface = get_surface_colors(appearance_mode, surface_theme)
        accent = get_accent_colors(color_theme)
        controls = get_control_colors(appearance_mode, surface_theme)
        try:
            self.tabs.configure(
                fg_color=surface["card_alt"],
                segmented_button_fg_color=surface["neutral"],
                segmented_button_selected_color=accent["primary"],
                segmented_button_selected_hover_color=accent["hover"],
                segmented_button_unselected_color=surface["neutral"],
                segmented_button_unselected_hover_color=surface["neutral_hover"],
                text_color=controls["text_color"],
            )
        except Exception:
            try:
                self.tabs.configure(fg_color=surface["card_alt"])
            except Exception:
                pass

        for control in (
            getattr(self, "appearance_combo", None),
            getattr(self, "color_theme_combo", None),
            getattr(self, "surface_theme_combo", None),
            getattr(self, "font_family_combo", None),
            getattr(self, "font_size_combo", None),
            getattr(self, "table_density_combo", None),
        ):
            if control is not None:
                control.apply_visual_preferences(
                    font_config=self.font_config,
                    color_theme=color_theme,
                    surface_theme=surface_theme,
                    appearance_mode=appearance_mode,
                )

        for frame_name in ("visual_scroll", "palette_group", "typography_group"):
            frame = getattr(self, frame_name, None)
            if frame is not None:
                try:
                    frame.configure(fg_color="transparent" if frame_name == "visual_scroll" else surface["card"])
                except Exception:
                    pass

        for label_name in ("palette_title", "typography_title"):
            label = getattr(self, label_name, None)
            if label is not None:
                try:
                    label.configure(
                        font=self.font_config.tuple("section", "bold"),
                        text_color=controls["text_color"],
                    )
                except Exception:
                    pass

    def collect_preferences(self) -> GuiPreferences:
        color_control = getattr(self, "color_theme_combo", None)
        surface_control = getattr(self, "surface_theme_combo", None)
        return GuiPreferences(
            appearance_mode=self.appearance_combo.get_label(),
            color_theme=(
                str(color_control.get_value())
                if color_control is not None
                else self.preferences.color_theme
            ),
            surface_theme=(
                str(surface_control.get_value())
                if surface_control is not None
                else self.preferences.surface_theme
            ),
            font_family=self.font_family_combo.get_label(),
            font_size=self.font_size_combo.get_label(),
            table_density=self.table_density_combo.get_label(),
        ).normalized()

    def apply(self) -> None:
        self.preferences = self.collect_preferences()
        self.apply_visual_preferences(
            self.font_config,
            self.preferences.color_theme,
            self.preferences.surface_theme,
            self.preferences.appearance_mode,
        )
        if callable(self.on_apply):
            self.on_apply(self.preferences)

    def accept(self) -> None:
        self.apply()
        self.close()


def show_settings_window(
    parent: Any,
    preferences: GuiPreferences | None = None,
    font_config: FontConfig | None = None,
    on_apply: PreferencesCallback | None = None,
    preference_mode: str = VISUAL_PREFERENCES_ADVANCED,
) -> SettingsWindow | None:
    resolved_mode = normalize_visual_preferences_mode(preference_mode)
    if resolved_mode == VISUAL_PREFERENCES_NONE:
        return None
    return SettingsWindow(
        parent,
        preferences=preferences,
        font_config=font_config,
        on_apply=on_apply,
        preference_mode=resolved_mode,
    )
