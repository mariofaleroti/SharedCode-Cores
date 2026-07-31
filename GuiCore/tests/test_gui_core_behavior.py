import pathlib
import unittest

from gui_core import (
    __version__,
    GUI_CORE_VERSION,
    DEFAULT_APPEARANCE_MODE,
    DEFAULT_COLOR_THEME,
    DEFAULT_SURFACE_THEME,
    APPEARANCE_LABEL_OPTIONS,
    COLOR_THEME_OPTIONS,
    SURFACE_THEME_OPTIONS,
    ButtonSpec,
    CardHeaderAction,
    ChoiceOption,
    KeyValueItem,
    MetricItem,
    TooltipSpec,
    VALID_STATE_KINDS,
    DialogButton,
    DialogSpec,
    COMFORTABLE_LAYOUT_PROFILE,
    COMPACT_LAYOUT_PROFILE,
    LAYOUT_PROFILE_NAMES,
    LabeledComboAction,
    LabeledComboBox,
    STANDARD_LAYOUT_PROFILE,
    FontConfig,
    GuiLayoutProfile,
    GuiActionButton,
    GuiAppConfig,
    WindowIconResult,
    GuiMenuItem,
    SidebarConfig,
    GuiPreferences,
    SecondaryWindowConfig,
    TableCell,
    TableColumn,
    TableSortState,
    ThemeConfig,
    build_restart_arguments,
    coerce_choice_options,
    coerce_key_value_items,
    coerce_metric_items,
    coerce_row_values,
    get_button_style_options,
    get_choice_labels,
    normalize_appearance_label,
    normalize_appearance_value,
    normalize_button_style,
    normalize_command_key,
    normalize_control_state,
    resolve_control_dimension,
    resolve_control_gap,
    normalize_color_theme,
    normalize_color_theme_label,
    normalize_surface_theme,
    normalize_surface_theme_label,
    normalize_picker_mode,
    normalize_selection_mode,
    normalize_state_kind,
    normalize_secondary_window_size,
    resolve_window_icon_path,
    set_window_icon_metadata,
    row_values_to_mapping,
    WindowConfig,
    build_about_message,
    build_help_message,
    calculate_center_geometry,
    get_accent_colors,
    get_surface_colors,
    get_font_role_size,
    get_layout_profile,
    get_results_density_row_height,
    get_table_colors,
    apply_window_icon,
    calculate_child_geometry,
    get_window_icon_metadata,
    is_customtkinter_available,
    normalize_appearance_mode,
    normalize_dialog_kind,
    normalize_layout_profile_name,
    normalize_table_density,
    normalize_window_size,
)
from gui_core.widgets.progress_panel import calculate_progress_value
from gui_core.widgets.results_table import build_heading_options


class GuiCoreTests(unittest.TestCase):
    def test_theme_config_defaults(self):
        config = ThemeConfig()
        self.assertEqual(config.appearance_mode, DEFAULT_APPEARANCE_MODE)
        self.assertEqual(config.color_theme, DEFAULT_COLOR_THEME)

    def test_window_config_to_dict_is_json_safe(self):
        config = WindowConfig(title="Tool")
        data = config.to_dict()
        self.assertEqual(data["title"], "Tool")
        self.assertIsInstance(data["resizable"], list)

    def test_normalize_window_size_enforces_minimum(self):
        width, height = normalize_window_size(100, 100)
        self.assertGreaterEqual(width, 800)
        self.assertGreaterEqual(height, 500)

    def test_calculate_center_geometry(self):
        geometry = calculate_center_geometry(1920, 1080, 1000, 600)
        self.assertEqual(geometry, "1000x600+460+240")

    def test_customtkinter_availability_returns_boolean(self):
        self.assertIsInstance(is_customtkinter_available(), bool)

    def test_gui_app_config_generates_window_config(self):
        config = GuiAppConfig(app_name="Event Health", app_subtitle="Diagnóstico", app_version="v0.1.0")
        window_config = config.to_window_config()
        self.assertEqual(window_config.title, "Event Health v0.1.0")
        self.assertEqual(config.to_dict()["footer_items"][0]["command_key"], "settings")
        self.assertTrue(config.to_dict()["restart_on_appearance_change"])
        self.assertEqual(config.to_dict()["restart_delay_ms"], 350)
        self.assertIsNone(config.to_dict()["icon_path"])
        self.assertIsNone(config.to_dict()["icon_png_path"])

    def test_layout_profile_names_and_aliases(self):
        self.assertEqual(LAYOUT_PROFILE_NAMES, ("compact", "standard", "comfortable"))
        self.assertEqual(normalize_layout_profile_name("Compacta"), "compact")
        self.assertEqual(normalize_layout_profile_name("Cómoda"), "comfortable")
        self.assertEqual(normalize_layout_profile_name("invalid"), "standard")

    def test_layout_profiles_are_ordered_by_density(self):
        self.assertLess(COMPACT_LAYOUT_PROFILE.control_height, STANDARD_LAYOUT_PROFILE.control_height)
        self.assertLess(STANDARD_LAYOUT_PROFILE.control_height, COMFORTABLE_LAYOUT_PROFILE.control_height)
        self.assertLess(COMPACT_LAYOUT_PROFILE.widget_gap, STANDARD_LAYOUT_PROFILE.widget_gap)
        self.assertLess(STANDARD_LAYOUT_PROFILE.widget_gap, COMFORTABLE_LAYOUT_PROFILE.widget_gap)
        self.assertEqual(STANDARD_LAYOUT_PROFILE.action_height, 34)
        self.assertEqual(STANDARD_LAYOUT_PROFILE.sidebar_padding, 14)

    def test_custom_layout_profile_is_json_safe(self):
        custom = GuiLayoutProfile(
            name="project_custom",
            control_height=30,
            action_height=36,
        )
        data = custom.to_dict()
        self.assertEqual(data["name"], "project_custom")
        self.assertEqual(data["control_height"], 30)
        self.assertIs(get_layout_profile(custom), custom)

    def test_invalid_custom_layout_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            GuiLayoutProfile(name="", control_height=28)
        with self.assertRaises(ValueError):
            GuiLayoutProfile(name="invalid", control_height=0)

    def test_gui_app_config_defaults_to_standard_layout(self):
        config = GuiAppConfig(app_name="Tool")
        self.assertEqual(config.resolved_layout_profile, STANDARD_LAYOUT_PROFILE)
        self.assertEqual(config.to_dict()["layout_profile"]["name"], "standard")
        compact = GuiAppConfig(app_name="Tool", layout_profile="compact")
        self.assertEqual(compact.resolved_layout_profile, COMPACT_LAYOUT_PROFILE)

    def test_font_config_applies_layout_offset_without_changing_default(self):
        standard = FontConfig(size_option="Normal")
        compact = standard.with_size_offset(COMPACT_LAYOUT_PROFILE.font_size_offset)
        comfortable = standard.with_size_offset(COMFORTABLE_LAYOUT_PROFILE.font_size_offset)
        self.assertEqual(standard.size("body"), 11)
        self.assertEqual(compact.size("body"), 10)
        self.assertEqual(comfortable.size("body"), 12)


    def test_sidebar_config_is_json_safe(self):
        sidebar = SidebarConfig(
            header_visible=False,
            footer_label_visible=False,
            footer_columns=2,
            primary_action_columns=2,
            scrollbar_width=8,
        )
        data = sidebar.to_dict()
        self.assertFalse(data["header_visible"])
        self.assertFalse(data["footer_label_visible"])
        self.assertEqual(data["footer_columns"], 2)
        self.assertEqual(data["primary_action_columns"], 2)
        self.assertEqual(data["scrollbar_width"], 8)

    def test_sidebar_config_rejects_invalid_geometry(self):
        with self.assertRaises(ValueError):
            SidebarConfig(footer_columns=0)
        with self.assertRaises(ValueError):
            SidebarConfig(primary_action_columns=5)
        with self.assertRaises(ValueError):
            SidebarConfig(scrollbar_width=0)

    def test_gui_app_config_serializes_sidebar_and_primary_actions(self):
        config = GuiAppConfig(
            app_name="Tool",
            sidebar_config=SidebarConfig(
                footer_columns=2,
                primary_action_columns=2,
            ),
            primary_actions=(
                GuiActionButton(
                    "Ejecutar",
                    "run",
                    style="primary",
                    icon_text="▶",
                ),
                GuiActionButton(
                    "Limpiar",
                    "clear",
                    style="secondary",
                ),
            ),
        )
        data = config.to_dict()
        self.assertEqual(data["sidebar_config"]["footer_columns"], 2)
        self.assertEqual(
            data["sidebar_config"]["primary_action_columns"],
            2,
        )
        self.assertEqual(
            data["primary_actions"][0]["command_key"],
            "run",
        )
        self.assertEqual(
            data["primary_actions"][0]["icon_text"],
            "▶",
        )
        self.assertEqual(
            data["primary_actions"][1]["style"],
            "secondary",
        )


    def test_control_dimension_helpers_validate_values(self):
        self.assertEqual(resolve_control_dimension(None, 26), 26)
        self.assertEqual(resolve_control_dimension(31, 26), 31)
        self.assertEqual(resolve_control_gap(None, 6), 6)
        self.assertEqual(resolve_control_gap(0, 6), 0)

        with self.assertRaises(ValueError):
            resolve_control_dimension(0, 26)
        with self.assertRaises(ValueError):
            resolve_control_gap(-1, 6)

    def test_compact_control_exports_are_public(self):
        self.assertTrue(callable(LabeledComboAction))
        self.assertTrue(callable(LabeledComboBox))


    def test_card_header_action_key_is_stable(self):
        action = CardHeaderAction("Abrir carpeta")
        self.assertEqual(action.key, "abrir_carpeta")
        explicit = CardHeaderAction(
            "Abrir",
            command_key="open",
        )
        self.assertEqual(explicit.key, "open")

    def test_state_kind_normalization(self):
        self.assertEqual(normalize_state_kind("WARNING"), "warning")
        self.assertEqual(normalize_state_kind("unknown"), "empty")
        self.assertIn("ready", VALID_STATE_KINDS)

    def test_key_value_items_accept_mapping_and_sequences(self):
        mapped = coerce_key_value_items(
            {"Estado": "Operativo", "Tarea": "Instalada"}
        )
        self.assertEqual(
            [item.field for item in mapped],
            ["Estado", "Tarea"],
        )

        items = coerce_key_value_items(
            (
                ("Errores", 0, "success"),
                {
                    "field": "Sincronización",
                    "value": "Correcta",
                    "semantic": "ready",
                },
                KeyValueItem("Rutas", 2),
            )
        )
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].semantic, "success")
        self.assertEqual(items[1].value, "Correcta")
        self.assertEqual(items[2].field, "Rutas")


    def test_tooltip_spec_is_json_safe_and_validated(self):
        spec = TooltipSpec(
            "Descripción",
            title="Ayuda",
            delay_ms=500,
            visible_ms=2500,
            wraplength=280,
        )
        data = spec.to_dict()
        self.assertEqual(data["text"], "Descripción")
        self.assertEqual(data["title"], "Ayuda")
        self.assertEqual(data["visible_ms"], 2500)

        with self.assertRaises(ValueError):
            TooltipSpec("Texto", delay_ms=-1)
        with self.assertRaises(ValueError):
            TooltipSpec("Texto", wraplength=0)

    def test_metric_items_accept_mapping_and_sequences(self):
        mapped = coerce_metric_items(
            {
                "Procesados": 120,
                "Advertencias": 2,
            }
        )
        self.assertEqual(
            [item.title for item in mapped],
            ["Procesados", "Advertencias"],
        )

        metrics = coerce_metric_items(
            (
                MetricItem(
                    "status",
                    "Estado",
                    "Operativo",
                    semantic="success",
                ),
                {
                    "key": "duration",
                    "title": "Duración",
                    "value": "00:32",
                    "tooltip": "Tiempo total.",
                },
                (
                    "errors",
                    "Errores",
                    0,
                    "Sin incidencias",
                    "success",
                ),
            )
        )
        self.assertEqual(len(metrics), 3)
        self.assertEqual(metrics[0].semantic, "success")
        self.assertEqual(metrics[1].tooltip, "Tiempo total.")
        self.assertEqual(metrics[2].detail, "Sin incidencias")

    def test_metric_item_rejects_empty_contract_fields(self):
        with self.assertRaises(ValueError):
            MetricItem("", "Estado", "OK")
        with self.assertRaises(ValueError):
            MetricItem("status", "", "OK")

    def test_restart_arguments_support_script_and_frozen_apps(self):
        script_args = build_restart_arguments(
            executable="python.exe",
            argv=["demo.py", "--flag"],
            frozen=False,
        )
        frozen_args = build_restart_arguments(
            executable="Tool.exe",
            argv=["Tool.exe", "--flag"],
            frozen=True,
        )

        self.assertEqual(script_args, ["python.exe", "demo.py", "--flag"])
        self.assertEqual(frozen_args, ["Tool.exe", "--flag"])

    def test_gui_preferences_are_json_safe_and_normalized(self):
        preferences = GuiPreferences(
            appearance_mode="Oscuro",
            color_theme="invalid",
            font_family="No existe",
            font_size="Gigante",
            table_density="Cómoda",
        ).normalized()
        data = preferences.to_dict()
        self.assertEqual(data["appearance_mode"], "dark")
        self.assertEqual(data["appearance_label"], "Oscuro")
        self.assertEqual(data["color_theme"], DEFAULT_COLOR_THEME)
        self.assertEqual(data["color_theme_label"], "Azul")
        self.assertEqual(data["surface_theme"], DEFAULT_SURFACE_THEME)
        self.assertEqual(data["surface_theme_label"], "Predeterminado")
        self.assertEqual(data["font_family"], "Segoe UI")
        self.assertEqual(data["font_size"], "Normal")
        self.assertEqual(data["table_density"], "Cómoda")
        self.assertIn("Oscuro", APPEARANCE_LABEL_OPTIONS)
        self.assertIn(DEFAULT_COLOR_THEME, COLOR_THEME_OPTIONS)
        self.assertIn("black", COLOR_THEME_OPTIONS)
        self.assertIn("graphite", COLOR_THEME_OPTIONS)
        self.assertIn("onyx", SURFACE_THEME_OPTIONS)

    def test_preference_normalizers(self):
        self.assertEqual(normalize_appearance_label("dark"), "Oscuro")
        self.assertEqual(normalize_appearance_value("Claro"), "light")
        self.assertEqual(normalize_color_theme("green"), "green")
        self.assertEqual(normalize_color_theme("Morado"), "purple")
        self.assertEqual(normalize_color_theme("Grafito"), "graphite")
        self.assertEqual(normalize_color_theme("Negro"), "black")
        self.assertEqual(normalize_color_theme("invalid"), DEFAULT_COLOR_THEME)
        self.assertEqual(normalize_color_theme_label("purple"), "Morado")
        self.assertEqual(normalize_color_theme_label("charcoal"), "Carbón")
        self.assertEqual(normalize_surface_theme("Ónix"), "onyx")
        self.assertEqual(normalize_surface_theme("invalid"), DEFAULT_SURFACE_THEME)
        self.assertEqual(normalize_surface_theme_label("forest"), "Bosque")
        self.assertEqual(normalize_table_density("Compacta"), "Compacta")
        self.assertEqual(normalize_table_density("invalid"), "Normal")

    def test_secondary_window_config_and_geometry_are_json_safe(self):
        config = SecondaryWindowConfig(title="Categorías", subtitle="Admin")
        data = config.to_dict()
        self.assertEqual(data["title"], "Categorías")
        self.assertIsInstance(data["resizable"], list)
        self.assertEqual(normalize_secondary_window_size(100, 100), (520, 360))
        self.assertEqual(calculate_child_geometry(1200, 800, 100, 50, 600, 400), "600x400+400+250")

    def test_gui_menu_item_key_is_stable(self):
        self.assertEqual(GuiMenuItem("Abrir carpeta").key, "abrir_carpeta")
        self.assertEqual(GuiMenuItem("Abrir carpeta", "open_folder").key, "open_folder")

    def test_font_config_role_sizes(self):
        font_config = FontConfig(size_option="Grande")
        self.assertEqual(font_config.size("body"), 12)
        self.assertEqual(get_font_role_size("No existe", "body"), 11)

    def test_results_density_row_height(self):
        self.assertEqual(get_results_density_row_height("Compacta"), 21)
        self.assertEqual(get_results_density_row_height("No existe"), 24)

    def test_appearance_mode_normalization(self):
        self.assertEqual(normalize_appearance_mode("Oscuro"), "dark")
        self.assertEqual(normalize_appearance_mode("Claro"), "light")
        self.assertEqual(normalize_appearance_mode("Sistema"), "system")

    def test_table_colors_have_required_keys(self):
        colors = get_table_colors("dark", "purple")
        for key in ("background", "foreground", "odd_row", "even_row", "selected_background"):
            self.assertIn(key, colors)
        self.assertEqual(colors["selected_background"], get_accent_colors("purple")["selected"])
        self.assertEqual(get_table_colors("dark", "black")["selected_background"], get_accent_colors("black")["selected"])
        self.assertEqual(get_table_colors("dark", "purple", "onyx")["background"], get_surface_colors("dark", "onyx")["table_background"])

    def test_table_column_to_dict(self):
        column = TableColumn("name", "Nombre", width=200, stretch=False)
        data = column.to_dict()
        self.assertEqual(data["key"], "name")
        self.assertFalse(data["stretch"])



    def test_heading_options_omit_command_when_sorting_is_disabled(self):
        column = TableColumn("status", "Estado")
        options = build_heading_options(
            column,
            enable_sorting=False,
            sort_callback=lambda _key: None,
        )

        self.assertEqual(options, {"text": "Estado"})
        self.assertNotIn("command", options)

    def test_heading_options_omit_command_for_non_sortable_column(self):
        column = TableColumn("status", "Estado", sortable=False)
        options = build_heading_options(
            column,
            enable_sorting=True,
            sort_callback=lambda _key: None,
        )

        self.assertEqual(options, {"text": "Estado"})
        self.assertNotIn("command", options)

    def test_heading_options_execute_sort_callback_for_sortable_column(self):
        selected = []
        column = TableColumn("status", "Estado")
        options = build_heading_options(
            column,
            enable_sorting=True,
            sort_callback=selected.append,
        )

        self.assertEqual(options["text"], "Estado")
        self.assertTrue(callable(options["command"]))
        options["command"]()
        self.assertEqual(selected, ["status"])

    def test_table_selection_mode_normalization(self):
        self.assertEqual(normalize_selection_mode("browse"), "browse")
        self.assertEqual(normalize_selection_mode("invalid"), "extended")
        self.assertEqual(normalize_selection_mode(None), "extended")

    def test_table_row_helpers_keep_column_order(self):
        columns = [TableColumn("index", "#"), TableColumn("name", "Nombre"), TableColumn("status", "Estado")]
        self.assertEqual(coerce_row_values({"status": "OK", "name": "Tool"}, columns), ["", "Tool", "OK"])
        self.assertEqual(coerce_row_values([1, "Tool"], columns), [1, "Tool", ""])
        self.assertEqual(row_values_to_mapping([1, "Tool", "OK"], columns), {"index": 1, "name": "Tool", "status": "OK"})

    def test_table_cell_and_sort_state_are_json_safe(self):
        cell = TableCell("item1", 0, "name", "Nombre", "Tool Alpha", {"name": "Tool Alpha"})
        self.assertEqual(cell.to_dict()["column_key"], "name")
        self.assertEqual(TableSortState("name", True).to_dict(), {"column_key": "name", "reverse": True})


    def test_sidebar_form_helpers_are_stable(self):
        self.assertEqual(normalize_command_key("Ejecutar demo"), "ejecutar_demo")
        self.assertEqual(normalize_button_style("danger"), "danger")
        self.assertEqual(normalize_button_style("unknown"), "primary")
        self.assertEqual(normalize_picker_mode("save-file"), "save_file")
        self.assertEqual(normalize_picker_mode("invalid"), "folder")
        self.assertEqual(normalize_control_state(False), "disabled")

    def test_choice_options_are_json_safe_and_unique(self):
        values = ["Carpeta", "Carpeta", ChoiceOption("Archivo", "file"), {"label": "Rápido", "value": "quick"}, ""]
        options = coerce_choice_options(values)
        self.assertEqual(get_choice_labels(values), ["Carpeta", "Archivo", "Rápido"])
        self.assertEqual(options[1].to_dict(), {"label": "Archivo", "value": "file"})

    def test_button_spec_and_style_options_are_json_safe(self):
        spec = ButtonSpec("Eliminar", style="danger", enabled=False)
        self.assertEqual(spec.to_dict()["command_key"], "eliminar")
        self.assertEqual(spec.to_dict()["style"], "danger")
        self.assertFalse(spec.to_dict()["enabled"])
        self.assertIn("fg_color", get_button_style_options("secondary"))
        self.assertEqual(get_button_style_options("primary", "orange")["fg_color"], get_accent_colors("orange")["primary"] )

    def test_progress_value_is_clamped(self):
        self.assertEqual(calculate_progress_value(50, 100), 0.5)
        self.assertEqual(calculate_progress_value(200, 100), 1.0)
        self.assertEqual(calculate_progress_value(-20, 100), 0.0)
        self.assertEqual(calculate_progress_value(10, 0), 0.0)

    def test_dialog_kind_normalization(self):
        self.assertEqual(normalize_dialog_kind("error"), "error")
        self.assertEqual(normalize_dialog_kind(" WARNING "), "warning")
        self.assertEqual(normalize_dialog_kind("unknown"), "info")
        self.assertEqual(normalize_dialog_kind(None), "info")

    def test_dialog_specs_are_json_safe(self):
        button = DialogButton("Continuar", True, "primary")
        spec = DialogSpec("Título", "Mensaje", kind="error", buttons=(button,))
        data = spec.to_dict()
        self.assertEqual(data["kind"], "error")
        self.assertEqual(data["buttons"][0]["text"], "Continuar")
        self.assertTrue(data["buttons"][0]["result"])

    def test_about_and_help_messages_can_be_customized(self):
        config = GuiAppConfig(
            app_name="Event Health",
            app_subtitle="Diagnóstico",
            app_version="v0.1.0",
            help_text="Ayuda propia",
            about_text="Texto extra",
        )
        self.assertIn("Event Health", build_about_message(config))
        self.assertIn("Texto extra", build_about_message(config))
        self.assertEqual(build_help_message(config), "Ayuda propia")
        self.assertEqual(config.to_dict()["help_text"], "Ayuda propia")

    def test_secondary_window_config_icon_fields_are_json_safe(self):
        config = SecondaryWindowConfig(
            title="Categorías",
            icon_path="assets/app_icon.ico",
            icon_png_path="assets/app_icon.png",
            inherit_parent_icon=True,
        )
        data = config.to_dict()
        self.assertEqual(data["icon_path"], "assets/app_icon.ico")
        self.assertEqual(data["icon_png_path"], "assets/app_icon.png")
        self.assertTrue(data["inherit_parent_icon"])

    def test_window_icon_resolution_prefers_png_on_linux(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            ico = Path(tmpdir) / "app.ico"
            png = Path(tmpdir) / "app.png"
            ico.write_bytes(b"ico")
            png.write_bytes(b"png")
            resolved = resolve_window_icon_path(ico, png, platform="linux")

        self.assertEqual(resolved.name, "app.png")

    def test_window_icon_resolution_prefers_ico_on_windows_when_available(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            ico = Path(tmpdir) / "app.ico"
            png = Path(tmpdir) / "app.png"
            ico.write_bytes(b"ico")
            png.write_bytes(b"png")
            resolved = resolve_window_icon_path(png, ico, platform="win32")

        self.assertEqual(resolved.name, "app.ico")

    def test_apply_window_icon_uses_iconbitmap_for_windows_ico(self):
        import tempfile
        from pathlib import Path

        class FakeWindow:
            def __init__(self):
                self.iconbitmap_calls = []
                self.iconphoto_calls = []

            def iconbitmap(self, path):
                self.iconbitmap_calls.append(path)

            def iconphoto(self, default, image):
                self.iconphoto_calls.append((default, image))

        with tempfile.TemporaryDirectory() as tmpdir:
            icon = Path(tmpdir) / "app.ico"
            icon.write_bytes(b"ico")
            window = FakeWindow()
            result = apply_window_icon(window, icon, platform="windows")

        self.assertTrue(result.applied)
        self.assertIsInstance(result, WindowIconResult)
        self.assertEqual(result.method, "iconbitmap")
        self.assertEqual(len(window.iconbitmap_calls), 1)
        self.assertEqual(len(window.iconphoto_calls), 0)

    def test_apply_window_icon_uses_iconphoto_for_png(self):
        import tempfile
        from pathlib import Path

        class FakeWindow:
            def __init__(self):
                self.iconbitmap_calls = []
                self.iconphoto_calls = []

            def iconbitmap(self, path):
                self.iconbitmap_calls.append(path)

            def iconphoto(self, default, image):
                self.iconphoto_calls.append((default, image))

        with tempfile.TemporaryDirectory() as tmpdir:
            icon = Path(tmpdir) / "app.png"
            icon.write_bytes(b"png")
            window = FakeWindow()
            result = apply_window_icon(window, icon, platform="linux", photo_image_factory=lambda path: "image")

        self.assertTrue(result.applied)
        self.assertEqual(result.method, "iconphoto")
        self.assertEqual(len(window.iconbitmap_calls), 0)
        self.assertEqual(window.iconphoto_calls, [(True, "image")])

    def test_window_icon_metadata_can_be_inherited(self):
        class FakeWindow:
            pass

        parent = FakeWindow()
        set_window_icon_metadata(parent, "assets/app.ico", "assets/app.png")
        self.assertEqual(get_window_icon_metadata(parent), ("assets/app.ico", "assets/app.png"))

    def test_window_icon_metadata_normalizes_windows_separators(self):
        class FakeWindow:
            pass

        parent = FakeWindow()
        set_window_icon_metadata(
            parent,
            r"assets\app.ico",
            r"assets\app.png",
        )
        self.assertEqual(
            get_window_icon_metadata(parent),
            ("assets/app.ico", "assets/app.png"),
        )



class GuiCorePreferenceStoreTests(unittest.TestCase):
    def test_preferences_json_store_roundtrip(self):
        import tempfile
        from pathlib import Path
        from gui_core import GuiPreferences, load_preferences_from_json, save_preferences_to_json

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "prefs.json"
            prefs = GuiPreferences(
                appearance_mode="Claro",
                color_theme="Morado",
                font_family="Consolas",
                font_size="Grande",
                table_density="Cómoda",
                surface_theme="Ónix",
            )
            save_preferences_to_json(path, prefs)
            loaded = load_preferences_from_json(path)

        self.assertEqual(loaded.appearance_mode, "light")
        self.assertEqual(loaded.color_theme, "purple")
        self.assertEqual(loaded.font_family, "Consolas")
        self.assertEqual(loaded.font_size, "Grande")
        self.assertEqual(loaded.table_density, "Cómoda")
        self.assertEqual(loaded.surface_theme, "onyx")

    def test_preferences_json_store_falls_back_on_missing_file(self):
        import tempfile
        from pathlib import Path
        from gui_core import GuiPreferences, load_preferences_from_json

        with tempfile.TemporaryDirectory() as tmpdir:
            loaded = load_preferences_from_json(Path(tmpdir) / "missing.json")

        self.assertEqual(loaded, GuiPreferences())

    def test_public_version_matches_current_development_line(self):
        self.assertEqual(__version__, "1.1.0.dev5")
        self.assertEqual(GUI_CORE_VERSION, __version__)

    def test_documentation_files_exist(self):
        project_root = pathlib.Path(__file__).resolve().parents[1]
        expected = [
            "README.md",
            "CHANGELOG.md",
            "docs/README.md",
            "docs/GUI_CONTRACT.md",
            "docs/QUICKSTART.md",
            "docs/COMPONENT_MAP.md",
            "docs/APP_TEMPLATE.md",
        ]
        for relative_path in expected:
            self.assertTrue((project_root / relative_path).exists(), relative_path)

    def test_public_exports_are_unique(self):
        import gui_core

        self.assertEqual(len(gui_core.__all__), len(set(gui_core.__all__)))
        self.assertIn("GuiAppWindow", gui_core.__all__)
        self.assertIn("GuiPreferences", gui_core.__all__)
        self.assertIn("ResultsTable", gui_core.__all__)


if __name__ == "__main__":
    unittest.main()


