# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for Sentopic Desktop Application
Handles complex dependencies including SQLAlchemy, sentence-transformers, and FastAPI
"""

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = os.path.dirname(os.path.abspath(SPEC))

# Model cache paths
huggingface_cache = os.path.expanduser('~/.cache/huggingface')
model_cache = os.path.join(huggingface_cache, 'hub')
model_name = 'models--sentence-transformers--all-MiniLM-L6-v2'
model_path = os.path.join(model_cache, model_name)

# Prepare data files to include
datas = []

# Include the sentence-transformer model if it exists
if os.path.exists(model_path):
    print(f"✅ Found sentence-transformer model at: {model_path}")
    datas.append((model_path, f'huggingface_cache/hub/{model_name}'))
else:
    print(f"⚠️  Sentence-transformer model not found at: {model_path}")
    print("   Model will be downloaded during first run")

# Include configuration files
config_example_path = os.path.join(project_root, 'config.example.json')
if os.path.exists(config_example_path):
    datas.append((config_example_path, '.'))

# Include actual config.json if it exists (for development testing)
config_path = os.path.join(project_root, 'config.json')
if os.path.exists(config_path):
    datas.append((config_path, '.'))
    print(f"✅ Including config.json in bundle")

# Hidden imports required for proper functionality
hiddenimports = [
    # SQLAlchemy database support
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.engine.default',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.sql.sqltypes',
    'sqlalchemy.pool',
    'sqlalchemy.orm',
    'sqlalchemy.ext.declarative',
    
    # FastAPI and Uvicorn server
    'uvicorn',
    'uvicorn.main',
    'uvicorn.server',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan.on',
    'uvicorn.loops.auto',
    'uvicorn.logging',
    
    # Sentence transformers and ML dependencies
    'sentence_transformers',
    'sentence_transformers.models',
    'sentence_transformers.models.Transformer',
    'sentence_transformers.models.Pooling',
    'sentence_transformers.models.Normalize',
    'transformers',
    'transformers.modeling_utils',
    'transformers.configuration_utils',
    'transformers.tokenization_utils',
    'torch',
    'torch.nn',
    'torch.nn.functional',
    'torch.optim',
    'torch.utils',
    'torch.utils.data',
    
    # NumPy and scientific computing
    'numpy',
    'numpy.core',
    'numpy.core._methods',
    'numpy.lib.format',
    
    # HTTP and networking
    'praw',
    'praw.models',
    'praw.config',
    'praw.reddit',
    'praw.util',
    'praw.util.deprecate_args',
    'praw.core',
    'praw.core.config',
    'anthropic',
    'openai',
    'requests',
    'urllib3',
    
    # Utilities
    'tqdm',
    'vaderSentiment',
    'vaderSentiment.vaderSentiment',
    'json',
    'datetime',
    'uuid',
    'signal',
    'multipart',
    'python_multipart',
]

# Packages to exclude (reduce bundle size)
excludes = [
    # GUI frameworks not needed
    'tkinter',
    'tkinter.ttk',
    'matplotlib.backends._backend_tk',
    
    # Large optional dependencies
    'IPython',
    'jupyter',
    'notebook',
    'scipy.spatial.distance',  # Large scipy component
    'PIL.ImageTk',  # Tkinter image support
    
    # Development tools
    'pytest',
    'setuptools',
    'pip',
    'wheel',
    
    # Documentation tools
    'sphinx',
    'docutils',
]

# Analysis configuration
a = Analysis(
    ['run_api.py'],  # Entry point script
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    optimize=0,
)

# Remove duplicate files and optimize
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='sentopic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable
    console=True,  # Keep console for debugging in development
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Collect all files into distribution directory
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='sentopic',
)

print("🔧 PyInstaller spec file loaded successfully")
print(f"📁 Project root: {project_root}")
print(f"📊 Data files included: {len(datas)}")
print(f"📦 Hidden imports: {len(hiddenimports)}")
print(f"🚫 Excluded packages: {len(excludes)}")