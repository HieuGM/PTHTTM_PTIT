"""Install absent or incompatible libraries into the current notebook kernel."""
import importlib.util
import importlib.metadata
import subprocess
import sys

if sys.version_info < (3, 11):
    raise RuntimeError('Cần Python >=3.11; khuyến nghị Python 3.12')
if importlib.util.find_spec('packaging') is None:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'packaging'])
from packaging.requirements import Requirement


def compatible(module, requirement):
    parsed = Requirement(requirement)
    try:
        return (importlib.util.find_spec(module) is not None and
                importlib.metadata.version(parsed.name) in parsed.specifier)
    except importlib.metadata.PackageNotFoundError:
        return False


if not compatible('torch', 'torch>=2.9,<3'):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'torch>=2.9,<3',
                           '--index-url', 'https://download.pytorch.org/whl/cpu'])
packages = {'numpy': 'numpy>=2.3,<3', 'pandas': 'pandas>=2.3,<4',
    'sklearn': 'scikit-learn>=1.7,<2', 'matplotlib': 'matplotlib>=3.10,<4',
    'fastapi': 'fastapi>=0.115,<1', 'pydantic': 'pydantic>=2.10,<3',
    'httpx': 'httpx>=0.27,<1', 'uvicorn': 'uvicorn>=0.30,<1',
    'ipywidgets': 'ipywidgets>=8,<9', 'bs4': 'beautifulsoup4>=4.12,<5',
    'pypdf': 'pypdf>=5,<7', 'neo4j': 'neo4j>=5.26,<7',
    'dotenv': 'python-dotenv>=1,<2', 'requests': 'requests>=2.32,<3'}
missing = [requirement for module, requirement in packages.items()
           if not compatible(module, requirement)]
if missing:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
print('Môi trường đã có thư viện tương thích. Nếu vừa nâng thư viện đã import, hãy Restart Kernel và Run All.')
