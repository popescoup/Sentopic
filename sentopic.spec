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

# Get site-packages directory for finding binaries
venv_path = os.path.join(project_root, 'sentopic-env')
if sys.platform == 'win32':
    site_packages = os.path.join(venv_path, 'Lib', 'site-packages')
else:
    # macOS/Linux
    python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    site_packages = os.path.join(venv_path, 'lib', python_version, 'site-packages')

print(f"📦 Site-packages path: {site_packages}")

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

# DO NOT include config.json in bundle - users will create their own in user data directory
# Only config.example.json should be bundled as a template

# Prepare binaries to include (CRITICAL FOR ML LIBRARIES)
binaries = []

# Include torch binaries (required for sentence-transformers)
torch_lib_path = os.path.join(site_packages, 'torch', 'lib')
if os.path.exists(torch_lib_path):
    print(f"✅ Found torch libraries at: {torch_lib_path}")
    # Explicitly add each torch library file
    import glob
    
    if sys.platform == 'darwin':  # macOS
        # Find all .dylib and .so files
        torch_dylibs = glob.glob(os.path.join(torch_lib_path, '*.dylib'))
        torch_sos = glob.glob(os.path.join(torch_lib_path, '*.so'))
        
        for lib in torch_dylibs + torch_sos:
            binaries.append((lib, 'torch/lib'))
        
        print(f"   Added {len(torch_dylibs)} .dylib files")
        print(f"   Added {len(torch_sos)} .so files")
        
    elif sys.platform == 'win32':  # Windows
        torch_dlls = glob.glob(os.path.join(torch_lib_path, '*.dll'))
        for lib in torch_dlls:
            binaries.append((lib, 'torch/lib'))
        print(f"   Added {len(torch_dlls)} .dll files")
        
    else:  # Linux
        torch_sos = glob.glob(os.path.join(torch_lib_path, '*.so'))
        for lib in torch_sos:
            binaries.append((lib, 'torch/lib'))
        print(f"   Added {len(torch_sos)} .so files")
else:
    print(f"⚠️  Torch libraries not found at: {torch_lib_path}")

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
    
    # Transformers library (CRITICAL - many submodules)
    'transformers',
    'transformers.modeling_utils',
    'transformers.configuration_utils',
    'transformers.tokenization_utils',
    'transformers.tokenization_utils_base',
    'transformers.models',
    'transformers.models.bert',
    'transformers.models.bert.modeling_bert',
    'transformers.models.bert.tokenization_bert',
    'transformers.models.bert.configuration_bert',
    'transformers.models.deepseek_v3',  # Required by transformers 4.52+ auto-registration
    'transformers.models.deepseek_v3.modeling_deepseek_v3',
    'transformers.models.deepseek_v3.configuration_deepseek_v3',
    
    # Tokenizers (CRITICAL)
    'tokenizers',
    'tokenizers.implementations',
    'tokenizers.models',
    'tokenizers.pre_tokenizers',
    'tokenizers.processors',
    'tokenizers.decoders',
    'tokenizers.normalizers',
    
    # PyTorch (CRITICAL - deep internals required)
    'torch',
    'torch.nn',
    'torch.nn.functional',
    'torch.nn.modules',
    'torch.nn.modules.activation',
    'torch.nn.modules.loss',
    'torch.optim',
    'torch.utils',
    'torch.utils.data',
    'torch._C',
    'torch._six',
    'torch.serialization',
    'torch.storage',
    'torch.backends',
    'torch.backends.cpu',
    
    # HuggingFace Hub (CRITICAL for model loading)
    'huggingface_hub',
    'huggingface_hub.file_download',
    'huggingface_hub.hf_api',
    'huggingface_hub.utils',
    'huggingface_hub.constants',
    
    # Supporting ML libraries
    'safetensors',
    'safetensors.torch',
    'regex',
    'filelock',
    'joblib',
    
    # NumPy and scientific computing
    'numpy',
    'numpy.core',
    'numpy.core._methods',
    'numpy.lib.format',
    'sklearn',
    'sklearn.utils',
    'sklearn.metrics',
    'sklearn.metrics.pairwise',
    'scipy',
    'scipy.sparse',
    'scipy.spatial',
    'scipy.spatial.distance',
    
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
    
    # Large optional dependencies we don't need
    'IPython',
    'jupyter',
    'notebook',
    'PIL.ImageTk',  # Tkinter image support
    
    # Development tools
    'pytest',
    'setuptools',
    'pip',
    'wheel',
    
    # Documentation tools
    'sphinx',
    'docutils',
    
    # NOTE: We cannot exclude torch.cuda even though we're not using GPU
    # because PyTorch's internal imports check for its existence
    # Excluding it causes "No module named 'torch.cuda'" errors
]

# Analysis configuration
a = Analysis(
    ['run_api.py'],  # Entry point script
    pathex=[project_root],
    binaries=binaries,  # NOW INCLUDES TORCH BINARIES
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[os.path.join(project_root, 'hooks')],  # Use custom hooks
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
print(f"🔗 Binaries included: {len(binaries)}")
print(f"📦 Hidden imports: {len(hiddenimports)}")
print(f"🚫 Excluded packages: {len(excludes)}")