"""Execute visible inline cells as isolated modules; no application .py files required."""
import sys
import types
from IPython.core.magic import register_cell_magic

# Module namespaces keep equal function names in different chapters independent.
# Every module's actual source is visible in the following code cells.
for package in ('app', 'app.ml', 'app.agents', 'app.knowledge'):
    module = types.ModuleType(package)
    module.__path__ = []
    module.__package__ = package
    sys.modules[package] = module
    if '.' in package:
        parent, child = package.rsplit('.', 1)
        setattr(sys.modules[parent], child, module)


@register_cell_magic
def diacare_module(name, cell):
    name = name.strip()
    if not name.startswith('app.') or not all(part.isidentifier() for part in name.split('.')):
        raise ValueError('Tên module không hợp lệ')
    module = types.ModuleType(name)
    module.__package__ = name.rsplit('.', 1)[0]
    module.__file__ = str(ROOT / (name.replace('.', '/') + '.py'))
    sys.modules[name] = module
    parent, child = name.rsplit('.', 1)
    setattr(sys.modules[parent], child, module)
    exec(compile(cell, module.__file__, 'exec'), module.__dict__)
    print('Đã nạp mã trong ô:', name)
