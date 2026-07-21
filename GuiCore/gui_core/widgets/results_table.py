from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence

from tkinter import ttk

from ..styles.colors import get_table_colors
from ..styles.fonts import FontConfig
from ..styles.table_style import get_results_density_row_height

VALID_SELECTION_MODES = {"browse", "extended", "none"}


RowCallback = Callable[[Mapping[str, Any]], None]
RowsCallback = Callable[[List[Mapping[str, Any]]], None]
CellCallback = Callable[["TableCell"], None]


@dataclass(frozen=True)
class TableColumn:
    """Declarative column contract for ResultsTable.

    The object describes only visual/table behavior. Business meaning stays in the
    tool that owns the data.
    """

    key: str
    title: str
    width: int = 160
    min_width: int = 80
    anchor: str = "w"
    stretch: bool = True
    sortable: bool = True
    tooltip: bool = True
    max_width: int | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "width": self.width,
            "min_width": self.min_width,
            "anchor": self.anchor,
            "stretch": self.stretch,
            "sortable": self.sortable,
            "tooltip": self.tooltip,
            "max_width": self.max_width,
        }


@dataclass(frozen=True)
class TableCell:
    """Cell identified from a click/double-click/tooltip operation."""

    row_id: str
    row_index: int
    column_key: str
    column_title: str
    value: Any
    row: Mapping[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "row_id": self.row_id,
            "row_index": self.row_index,
            "column_key": self.column_key,
            "column_title": self.column_title,
            "value": self.value,
            "row": dict(self.row),
        }


@dataclass(frozen=True)
class TableSortState:
    """Current sorting state of a reusable ResultsTable."""

    column_key: str
    reverse: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {"column_key": self.column_key, "reverse": self.reverse}


def normalize_selection_mode(selection_mode: str | None) -> str:
    """Normalize Treeview selection modes without leaking tkinter details."""

    value = str(selection_mode or "extended").lower().strip()
    if value not in VALID_SELECTION_MODES:
        return "extended"
    return value


def coerce_row_values(row: Mapping[str, Any] | Sequence[Any], columns: Sequence[TableColumn]) -> List[Any]:
    """Return row values ordered exactly as the configured columns."""

    if isinstance(row, Mapping):
        return [row.get(column.key, "") for column in columns]

    values = list(row)
    if len(values) < len(columns):
        values.extend([""] * (len(columns) - len(values)))
    return values[: len(columns)]


def row_values_to_mapping(values: Sequence[Any], columns: Sequence[TableColumn]) -> Dict[str, Any]:
    """Convert ordered Treeview values back to a stable column-key mapping."""

    return {column.key: values[index] if index < len(values) else "" for index, column in enumerate(columns)}


def get_sortable_value(value: Any) -> tuple[int, Any]:
    """Return a stable sortable value that handles numbers and text gracefully."""

    if value is None:
        return (2, "")
    if isinstance(value, (int, float)):
        return (0, value)

    text = str(value).strip()
    if not text:
        return (2, "")

    normalized = text.replace(".", "", 1).replace(",", ".", 1)
    try:
        return (0, float(normalized))
    except ValueError:
        return (1, text.casefold())


class TreeviewCellTooltip:
    """Small tooltip for table cells whose text does not fit in the column."""

    def __init__(
        self,
        treeview: ttk.Treeview,
        columns: Sequence[TableColumn],
        get_font_callback: Callable[[], tuple] | None = None,
        get_colors_callback: Callable[[], Mapping[str, str]] | None = None,
    ) -> None:
        self.treeview = treeview
        self.columns = list(columns)
        self.get_font_callback = get_font_callback
        self.get_colors_callback = get_colors_callback
        self.tooltip_window = None
        self.tooltip_label = None
        self.current_cell = None
        self.treeview.bind("<Motion>", self.on_motion, add="+")
        self.treeview.bind("<Leave>", lambda _event: self.hide(), add="+")
        self.treeview.bind("<ButtonPress>", lambda _event: self.hide(), add="+")
        self.treeview.bind("<MouseWheel>", lambda _event: self.hide(), add="+")

    def get_colors(self) -> Mapping[str, str]:
        if callable(self.get_colors_callback):
            return self.get_colors_callback()
        return get_table_colors("dark")

    def on_motion(self, event: Any) -> None:
        row_id = self.treeview.identify_row(event.y)
        column_id = self.treeview.identify_column(event.x)
        if not row_id or not column_id:
            self.hide()
            return

        cell = (row_id, column_id)
        if cell == self.current_cell:
            return
        self.current_cell = cell

        try:
            column_index = int(column_id.replace("#", "")) - 1
            column = self.columns[column_index]
            values = self.treeview.item(row_id, "values")
            text = str(values[column_index])
        except Exception:
            self.hide()
            return

        if not column.tooltip or not text:
            self.hide()
            return

        if not self._should_show_tooltip(column.key, text):
            self.hide()
            return

        self.show(event.x_root + 14, event.y_root + 12, text)

    def _should_show_tooltip(self, column_key: str, text: str) -> bool:
        try:
            column_width = int(self.treeview.column(column_key, "width") or 0)
        except Exception:
            column_width = 0

        if column_width <= 0:
            return len(text) >= 45

        try:
            import tkinter.font as tkfont

            font = tkfont.Font(font=self.get_font_callback() if callable(self.get_font_callback) else None)
            return font.measure(text) > max(column_width - 16, 20)
        except Exception:
            return len(text) >= 45

    def show(self, x: int, y: int, text: str) -> None:
        self.hide()
        colors = self.get_colors()
        try:
            import tkinter as tk

            tooltip = tk.Toplevel(self.treeview)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(
                tooltip,
                text=text,
                justify="left",
                background=colors.get("heading_background", "#2b2b2b"),
                foreground=colors.get("heading_foreground", "#f2f2f2"),
                relief="solid",
                borderwidth=1,
                padx=8,
                pady=5,
                wraplength=680,
                font=self.get_font_callback() if callable(self.get_font_callback) else None,
            )
            label.pack()
            self.tooltip_window = tooltip
            self.tooltip_label = label
        except Exception:
            self.tooltip_window = None
            self.tooltip_label = None

    def hide(self) -> None:
        if self.tooltip_window is not None:
            try:
                self.tooltip_window.destroy()
            except Exception:
                pass
        self.tooltip_window = None
        self.tooltip_label = None
        self.current_cell = None


class ResultsTable:
    """Reusable ttk.Treeview table with SmartFilter-inspired behavior.

    Responsibilities:
    - visual table layout and style;
    - stable column contract;
    - row selection/double-click callbacks;
    - cell tooltips;
    - optional heading sorting;
    - column width helpers.

    It intentionally does not know what the rows mean.
    """

    def __init__(
        self,
        parent: Any,
        columns: Sequence[TableColumn],
        font_config: FontConfig | None = None,
        density: str = "Normal",
        style_name: str = "GuiCore.Treeview",
        appearance_mode_provider: Callable[[], str] | None = None,
        color_theme_provider: Callable[[], str] | None = None,
        surface_theme_provider: Callable[[], str] | None = None,
        enable_tooltips: bool = True,
        enable_sorting: bool = True,
        selection_mode: str = "extended",
        on_select: RowsCallback | None = None,
        on_row_click: CellCallback | None = None,
        on_double_click: CellCallback | None = None,
    ) -> None:
        self.columns = list(columns)
        self.font_config = font_config or FontConfig()
        self.density = density
        self.style_name = style_name
        self.appearance_mode_provider = appearance_mode_provider or (lambda: "dark")
        self.color_theme_provider = color_theme_provider or (lambda: "blue")
        self.surface_theme_provider = surface_theme_provider or (lambda: "default")
        self.enable_sorting = enable_sorting
        self.on_select = on_select
        self.on_row_click = on_row_click
        self.on_double_click = on_double_click
        self.sort_state: TableSortState | None = None
        self._row_data: Dict[str, Dict[str, Any]] = {}
        self._current_rows: List[Mapping[str, Any] | Sequence[Any]] = []

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.configure_style()

        try:
            parent.grid_rowconfigure(0, weight=1)
            parent.grid_columnconfigure(0, weight=1)
        except Exception:
            pass

        column_keys = [column.key for column in self.columns]
        self.tree = ttk.Treeview(
            parent,
            columns=column_keys,
            show="headings",
            style=self.style_name,
            selectmode=normalize_selection_mode(selection_mode),
        )
        self.vertical_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.horizontal_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        self.horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self._apply_columns()
        self._configure_row_tags()
        self._bind_events()

        self.tooltip = None
        if enable_tooltips:
            self.tooltip = TreeviewCellTooltip(
                self.tree,
                self.columns,
                get_font_callback=lambda: self.font_config.tuple("small"),
                get_colors_callback=self.get_colors,
            )

    def get_colors(self) -> Mapping[str, str]:
        return get_table_colors(self.appearance_mode_provider(), self.color_theme_provider(), self.surface_theme_provider())

    def configure_style(self) -> None:
        colors = self.get_colors()
        row_height = get_results_density_row_height(self.density)
        self.style.configure(
            self.style_name,
            background=colors["background"],
            foreground=colors["foreground"],
            rowheight=row_height,
            fieldbackground=colors["fieldbackground"],
            borderwidth=0,
            font=self.font_config.tuple("table"),
        )
        self.style.configure(
            f"{self.style_name}.Heading",
            background=colors["heading_background"],
            foreground=colors["heading_foreground"],
            font=self.font_config.tuple("table_heading", "bold"),
        )
        self.style.map(
            self.style_name,
            background=[("selected", colors["selected_background"])],
            foreground=[("selected", colors["selected_foreground"])],
        )

    def refresh_style(self) -> None:
        """Re-apply colors and row tags after a theme/font change."""

        self.configure_style()
        self._configure_row_tags()

    def _configure_row_tags(self) -> None:
        colors = self.get_colors()
        self.tree.tag_configure("odd", background=colors["odd_row"], foreground=colors["foreground"])
        self.tree.tag_configure("even", background=colors["even_row"], foreground=colors["foreground"])

    def _apply_columns(self) -> None:
        self.tree.configure(columns=[column.key for column in self.columns])
        for column in self.columns:
            command = None
            if self.enable_sorting and column.sortable:
                command = lambda key=column.key: self.sort_by_column(key)
            self.tree.heading(column.key, text=column.title, command=command)
            self.tree.column(
                column.key,
                width=column.width,
                minwidth=column.min_width,
                anchor=column.anchor,
                stretch=column.stretch,
            )

    def _bind_events(self) -> None:
        self.tree.bind("<<TreeviewSelect>>", self._handle_selection, add="+")
        self.tree.bind("<ButtonRelease-1>", self._handle_row_click, add="+")
        self.tree.bind("<Double-1>", self._handle_double_click, add="+")
        self.tree.bind("<Shift-MouseWheel>", self._handle_horizontal_mousewheel, add="+")
        self.tree.bind("<Shift-Button-4>", lambda _event: self.tree.xview_scroll(-3, "units"), add="+")
        self.tree.bind("<Shift-Button-5>", lambda _event: self.tree.xview_scroll(3, "units"), add="+")

    def _handle_horizontal_mousewheel(self, event: Any) -> str:
        delta = getattr(event, "delta", 0)
        if delta:
            self.tree.xview_scroll(-1 * int(delta / 120), "units")
        return "break"

    def _handle_selection(self, _event: Any) -> None:
        if callable(self.on_select):
            self.on_select(self.get_selected_rows())

    def _handle_row_click(self, event: Any) -> None:
        cell = self.identify_cell(event.x, event.y)
        if cell and callable(self.on_row_click):
            self.on_row_click(cell)

    def _handle_double_click(self, event: Any) -> None:
        cell = self.identify_cell(event.x, event.y)
        if cell and callable(self.on_double_click):
            self.on_double_click(cell)

    def configure_columns(self, columns: Sequence[TableColumn]) -> None:
        """Replace columns while preserving current rows when possible."""

        current_rows = list(self._current_rows)
        self.columns = list(columns)
        self._apply_columns()
        self.set_rows(current_rows)

    def clear(self) -> None:
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)
        self._row_data.clear()

    def set_rows(self, rows: Iterable[Mapping[str, Any] | Sequence[Any]]) -> None:
        self.clear()
        self._current_rows = list(rows)
        for index, row in enumerate(self._current_rows):
            values = coerce_row_values(row, self.columns)
            row_mapping = row_values_to_mapping(values, self.columns)
            item_id = self.tree.insert("", "end", values=values, tags=("odd" if index % 2 == 0 else "even",))
            self._row_data[item_id] = row_mapping

    def append_rows(self, rows: Iterable[Mapping[str, Any] | Sequence[Any]]) -> None:
        rows_to_add = list(rows)
        start_index = len(self._current_rows)
        self._current_rows.extend(rows_to_add)
        for offset, row in enumerate(rows_to_add):
            index = start_index + offset
            values = coerce_row_values(row, self.columns)
            row_mapping = row_values_to_mapping(values, self.columns)
            item_id = self.tree.insert("", "end", values=values, tags=("odd" if index % 2 == 0 else "even",))
            self._row_data[item_id] = row_mapping

    def get_row_count(self) -> int:
        return len(self.tree.get_children())

    def get_selected_values(self) -> List[tuple[Any, ...]]:
        values = []
        for item_id in self.tree.selection():
            values.append(tuple(self.tree.item(item_id, "values")))
        return values

    def get_selected_rows(self) -> List[Mapping[str, Any]]:
        return [self.get_row(item_id) for item_id in self.tree.selection()]

    def get_selected_row(self) -> Mapping[str, Any] | None:
        selected_rows = self.get_selected_rows()
        return selected_rows[0] if selected_rows else None

    def get_focused_row(self) -> Mapping[str, Any] | None:
        item_id = self.tree.focus()
        if not item_id:
            return None
        return self.get_row(item_id)

    def get_row(self, item_id: str) -> Mapping[str, Any]:
        if item_id in self._row_data:
            return dict(self._row_data[item_id])
        return row_values_to_mapping(self.tree.item(item_id, "values"), self.columns)

    def identify_cell(self, x: int, y: int) -> TableCell | None:
        row_id = self.tree.identify_row(y)
        column_id = self.tree.identify_column(x)
        if not row_id or not column_id:
            return None
        try:
            column_index = int(column_id.replace("#", "")) - 1
            column = self.columns[column_index]
            values = self.tree.item(row_id, "values")
            row_ids = list(self.tree.get_children())
            row = self.get_row(row_id)
            return TableCell(
                row_id=row_id,
                row_index=row_ids.index(row_id),
                column_key=column.key,
                column_title=column.title,
                value=values[column_index] if column_index < len(values) else "",
                row=row,
            )
        except Exception:
            return None

    def set_column_widths(self, widths: Mapping[str, int]) -> None:
        """Apply explicit widths by column key."""

        for column in self.columns:
            if column.key in widths:
                self.tree.column(column.key, width=max(int(widths[column.key]), column.min_width))

    def auto_size_columns(self, max_width: int = 520, padding: int = 32, include_rows: int = 200) -> None:
        """Resize columns based on heading and visible row content.

        This is a helper for product-like tables. It is intentionally conservative
        so long text still uses horizontal scroll instead of expanding forever.
        """

        try:
            import tkinter.font as tkfont

            body_font = tkfont.Font(font=self.font_config.tuple("table"))
            heading_font = tkfont.Font(font=self.font_config.tuple("table_heading", "bold"))
        except Exception:
            return

        children = list(self.tree.get_children())[:include_rows]
        for column_index, column in enumerate(self.columns):
            measured_width = heading_font.measure(column.title) + padding
            for item_id in children:
                values = self.tree.item(item_id, "values")
                text = str(values[column_index]) if column_index < len(values) else ""
                measured_width = max(measured_width, body_font.measure(text) + padding)

            effective_max = column.max_width or max_width
            final_width = max(column.min_width, min(measured_width, effective_max))
            self.tree.column(column.key, width=final_width)

    def sort_by_column(self, column_key: str, reverse: bool | None = None) -> None:
        """Sort current rows by a configured column key."""

        if column_key not in {column.key for column in self.columns}:
            return

        if reverse is None:
            reverse = bool(self.sort_state and self.sort_state.column_key == column_key and not self.sort_state.reverse)

        rows = [self.get_row(item_id) for item_id in self.tree.get_children()]
        rows.sort(key=lambda row: get_sortable_value(row.get(column_key)), reverse=reverse)
        self.sort_state = TableSortState(column_key=column_key, reverse=reverse)
        self.set_rows(rows)


    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        density: str | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        """Apply shared visual preferences to an existing table."""

        if font_config is not None:
            self.font_config = font_config
        if density is not None:
            self.density = str(density)
        if color_theme is not None:
            self.color_theme_provider = lambda value=str(color_theme): value
        if surface_theme is not None:
            self.surface_theme_provider = lambda value=str(surface_theme): value
        if appearance_mode is not None:
            self.appearance_mode_provider = lambda value=str(appearance_mode): value
        self.refresh_style()

    def set_on_select(self, callback: RowsCallback | None) -> None:
        self.on_select = callback

    def set_on_row_click(self, callback: CellCallback | None) -> None:
        self.on_row_click = callback

    def set_on_double_click(self, callback: CellCallback | None) -> None:
        self.on_double_click = callback
