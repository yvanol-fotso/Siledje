# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Inclure tous les fichiers PySide6
datas_pyside6, binaries_pyside6, hiddenimports_pyside6 = collect_all('PySide6')

a = Analysis(
    ['main.py'],
    pathex=[
        'C:\\Users\\fotyv\\Documents\\Boite\\yva_siledje\\librairie_papeterie\\librairie_papeterie\\src',
        'C:\\Users\\fotyv\\Documents\\Boite\\yva_siledje\\librairie_papeterie\\librairie_papeterie',
    ],
    binaries=binaries_pyside6,
    datas=datas_pyside6 + [
        # Icônes et styles QSS
        ('..\\assets', 'assets'),
        # Données dummy
        ('..\\data', 'data'),
        # Base de données SQLite
        ('..\\librairie.db', '.'),
    ],
    hiddenimports=[
        'PySide6.QtPrintSupport',
        'PySide6.QtSvg',
        'PySide6.QtXml',
        'psutil'
    ] + hiddenimports_pyside6,
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
    a.binaries,
    a.datas,
    [],
    name='LibrairiePapeterie',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,        # Mettre à False si tu veux pas de console noire
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)