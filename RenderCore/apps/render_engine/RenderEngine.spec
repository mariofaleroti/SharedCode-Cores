# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

project_root = Path.cwd()
render_core_data = collect_data_files("render_core", includes=["templates/**/*"])

block_cipher = None


a = Analysis(
    [str(project_root / "apps" / "render_engine" / "render_engine.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=render_core_data,
    hiddenimports=["jinja2", "openpyxl", "json_contract_core", "json_contract_core.api"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RenderEngine",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="RenderEngine",
)
