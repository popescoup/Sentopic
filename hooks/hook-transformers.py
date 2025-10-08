"""
PyInstaller hook for transformers library
Auto-discovers and includes all model modules
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata

# Collect all transformers submodules (including all model architectures)
hiddenimports = collect_submodules('transformers')

# Also collect data files (model configs, etc.)
datas = collect_data_files('transformers')

# CRITICAL: Include package metadata for ALL dependencies
# This prevents "distribution not found" errors
ml_packages = [
    'transformers',
    'sentence-transformers', 
    'torch',
    'tokenizers',
    'huggingface-hub',
    'safetensors',
    'tqdm',
    'regex',
    'filelock',
    'numpy',
    'requests',
    'urllib3',
    'certifi',
    'charset-normalizer',
    'idna',
    'packaging',
    'pyyaml',
    'sympy',
    'networkx',
    'jinja2',
    'markupsafe',
    'fsspec',
    'mpmath',
]

for package in ml_packages:
    try:
        datas += copy_metadata(package)
    except Exception:
        # Package might not be installed, skip it
        pass