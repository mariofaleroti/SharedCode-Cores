# Mapa de componentes GuiCore v0.1

## App

| Componente | Uso |
|---|---|
| `GuiAppConfig` | Contrato declarativo de la app. Nombre, versión, sidebar, preferencias y textos comunes. |
| `GuiAppWindow` | Ventana principal reusable con sidebar, contenido, progreso, tabla y status. |
| `GuiPreferences` | Preferencias visuales normalizadas. |

## Sidebar

| Componente | Uso |
|---|---|
| `Sidebar` | Contenedor lateral izquierdo. |
| `SidebarFormSection` | Sección de formulario dentro del sidebar. |
| `LabeledEntry` | Campo de texto con etiqueta. |
| `LabeledComboBox` | Combo con etiqueta. |
| `PathPicker` | Selector de carpeta/archivo/ruta. |
| `LabeledCheckBox` | Checkbox con etiqueta. |
| `LabeledSwitch` | Switch con etiqueta. |
| `ActionButton` | Botón estándar. |
| `ButtonRow` | Fila de botones. |

## Contenido

| Componente | Uso |
|---|---|
| `ContentPanel` | Área principal derecha. |
| `SectionCard` | Card/panel reusable. |
| `ProgressPanel` | Progreso de operación activa. |
| `StatusBar` | Estado general inferior. |

## Resultados

| Componente | Uso |
|---|---|
| `ResultsTable` | Tabla reusable basada en `ttk.Treeview`. |
| `TableColumn` | Definición declarativa de columna. |
| `TableCell` | Información de celda para callbacks. |
| `TableSortState` | Estado de orden de tabla. |

## Diálogos

| Componente | Uso |
|---|---|
| `show_info_dialog` | Mensaje informativo. |
| `show_success_dialog` | Mensaje de éxito. |
| `show_warning_dialog` | Advertencia. |
| `show_error_dialog` | Error con detalle técnico opcional. |
| `show_confirm_dialog` | Confirmación True/False. |
| `show_text_input_dialog` | Entrada simple. |
| `show_help_dialog` | Ayuda. |
| `show_about_dialog` | Acerca de. |
| `DialogSpec` | Diálogo declarativo avanzado. |
| `DialogButton` | Botón declarativo de diálogo. |

## Ventanas secundarias

| Componente | Uso |
|---|---|
| `SecondaryWindow` | Ventana secundaria completa. |
| `SecondaryWindowConfig` | Configuración de ventana secundaria. |
| `SettingsWindow` | Ventana de configuración visual común. |

## Estilos

| Componente | Uso |
|---|---|
| `FontConfig` | Familia y tamaño de fuente por roles. |
| `get_accent_colors` | Colores de acento. |
| `get_surface_colors` | Colores base/superficie. |
| `get_table_colors` | Colores de tabla. |
| `get_results_density_row_height` | Alto de fila según densidad. |

## Persistencia

| Componente | Uso |
|---|---|
| `load_preferences_from_json` | Leer preferencias visuales desde JSON. |
| `save_preferences_to_json` | Guardar preferencias visuales a JSON. |

## Compatibilidad inicial

| Componente | Uso |
|---|---|
| `WindowConfig` | Configuración mínima de ventana. |
| `ThemeConfig` | Configuración mínima de tema. |
| `create_main_window` | Factory simple original. |
| `apply_theme` | Aplicación inicial de tema CustomTkinter. |


| `window_icon.py` | Aplica iconos de ventana Windows/Linux y permite herencia desde ventana principal hacia secundarias. |
