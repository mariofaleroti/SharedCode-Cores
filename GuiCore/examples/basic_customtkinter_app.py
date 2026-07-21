from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from gui_core import ThemeConfig, WindowConfig, create_main_window, require_customtkinter

ctk = require_customtkinter()

window = create_main_window(
    WindowConfig(title="SharedCode Tool", width=1100, height=700),
    ThemeConfig(appearance_mode="dark", color_theme="blue"),
)

frame = ctk.CTkFrame(window, corner_radius=16)
frame.pack(fill="both", expand=True, padx=24, pady=24)

label = ctk.CTkLabel(
    frame,
    text="GuiCore + CustomTkinter",
    font=ctk.CTkFont(size=28, weight="bold"),
)
label.pack(pady=(32, 8))

subtitle = ctk.CTkLabel(
    frame,
    text="Base visual moderna para herramientas del ecosistema.",
    font=ctk.CTkFont(size=16),
)
subtitle.pack(pady=(0, 24))

button = ctk.CTkButton(frame, text="Cerrar", command=window.destroy)
button.pack()

window.mainloop()
