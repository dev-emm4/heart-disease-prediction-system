import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

a = Analysis(
    ['src/main.py'],                        # your entry point
    pathex=['.'],                       # look for imports here
    binaries=[],
    datas=[
    ('src/domain/predictionModel/DecisionTree.onnx', '.'),
    ('src/domain/predictionModel/NaiveBayes.onnx',     '.'),
    ('src/domain/predictionModel/SVM.onnx', '.'),
    ],
    hiddenimports=[
        'onnxruntime',
        'sklearn.utils._cython_blas',
        'sklearn.neighbors._partition_nodes',
        'sklearn.tree._utils',
    ],
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
    name='CardioAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,      # False = no terminal window pops up behind the app
    icon=None,          # replace with 'assets/icon.ico' if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CardioAI',
)