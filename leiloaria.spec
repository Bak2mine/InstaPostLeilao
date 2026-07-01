# PyInstaller spec file for Leiloaria Property PDF Generator
# Includes all PPTX templates and data files in the executable
# Build with: pyinstaller leiloaria.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('.', 'Post')],  # Bundle entire Post folder into 'Post' directory in EXE
    hiddenimports=[
        'pptx',
        'pptx.util',
        'pptx.dml.color',
        'PIL',
        'PIL.Image',
        'bs4',
        'lxml',
        'lxml.etree',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='leiloaria-generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console window for output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
