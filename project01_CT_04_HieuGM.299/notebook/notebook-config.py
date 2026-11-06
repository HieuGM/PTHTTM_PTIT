"""Notebook configuration: independent outputs and opt-in external credentials."""
from pathlib import Path
import base64, hashlib, json, os, platform, time
for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(variable, '2')
import numpy as np, pandas as pd, torch, sklearn
from IPython.display import display, Markdown, Image

RUN_MODE = os.getenv('DIACARE_RUN_MODE', 'full')  # Chọn 'smoke' để chạy24lượt nhanh.
USE_FPT = False  # Đổi True để chủ động gọi API; có thể phát sinh phí tài khoản FPT.
REFRESH_WEB = False  # Đổi True để tải lại Web/PDF thay snapshot tri thức nhúng.
INITIALIZE_NEO4J = False  # Chỉ True với database riêng dành cho bài này.
assert RUN_MODE in {'full', 'smoke'}
ROOT = Path(os.getenv('DIACARE_NOTEBOOK_OUTPUT', str(Path.cwd()/'diacare-notebook-output'))).resolve()
for folder in ('data/raw', 'data/database', 'models', 'results', 'app/knowledge', 'app/static'):
    (ROOT/folder).mkdir(parents=True, exist_ok=True)
os.environ['APP_DATA_DIR'] = str(ROOT/'runtime')
os.environ.pop('AUDIT_LOG_PATH', None)
torch.set_num_threads(2)
if USE_FPT:
    import getpass
    if not os.getenv('FPT_API_KEY'):
        os.environ['FPT_API_KEY'] = getpass.getpass('FPT_API_KEY (ẩn): ')
    os.environ.setdefault('FPT_MODEL', 'DeepSeek-V4.1-Flash')
    os.environ.setdefault('FPT_API_URL', 'https://mkp-api.fptcloud.com/chat/completions')
else:
    # Không tự gọi API chỉ vì máy đang có key trong environment.
    os.environ['FPT_API_KEY'] = ''
environment = {'python':platform.python_version(), 'torch':torch.__version__,
    'numpy':np.__version__, 'pandas':pd.__version__, 'sklearn':sklearn.__version__,
    'run_mode':RUN_MODE, 'use_fpt':USE_FPT, 'platform':platform.platform()}
(ROOT/'results/notebook-environment.json').write_text(json.dumps(environment, indent=2), encoding='utf-8')
display(environment)

