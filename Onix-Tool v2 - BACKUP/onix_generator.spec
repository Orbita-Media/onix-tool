# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['onix_generator.py'],
    pathex=[],
    binaries=[],
    datas=[('ONIX_BookProduct_3.0_reference.xsd', '.'), ('ONIX_BookProduct_CodeLists.xsd', '.'), ('ONIX_XHTML_Subset.xsd', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='onix_generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
