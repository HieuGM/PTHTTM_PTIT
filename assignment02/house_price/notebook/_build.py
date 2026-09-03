# -*- coding: utf-8 -*-
"""Build notebook: create .ipynb from source (marker #%% / #%% [md]), execute, save with outputs.

Cell rule: every `#%%` marker CLOSES the previous cell (flush current buffer as a cell)
and starts a new one of the given kind. Works for md-md, code-code, and mixed sequences.
"""
import sys
import pathlib
import nbformat as nbf
from nbclient import NotebookClient

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "diabetes_nb_source.py")
OUT = SRC.with_suffix(".ipynb")

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12.0"},
}

lines = SRC.read_text(encoding="utf-8").splitlines()
cells: list = []
buf: list = []
cur_kind = None  # None | "code" | "md"

def flush():
    """Emit the current buffer as a cell of cur_kind, then clear."""
    global buf
    if cur_kind is not None and buf:
        src = "\n".join(buf).strip("\n")
        if src.strip():
            cells.append(nbf.v4.new_code_cell(src) if cur_kind == "code"
                         else nbf.v4.new_markdown_cell(src))
        buf = []

for line in lines:
    if line.startswith("#%% [md]"):
        flush()
        cur_kind = "md"
    elif line.startswith("#%%"):
        flush()
        cur_kind = "code"
    else:
        if cur_kind == "md":
            buf.append(line[1:] if line.startswith("#") else line)
        elif cur_kind == "code":
            buf.append(line)
flush()
nb.cells = cells
nbf.write(nb, OUT)
print(f"notebook written: {OUT} with {len(cells)} cells")

client = NotebookClient(nb, timeout=1200, kernel_name="python3",
                        resources={"metadata": {"path": str(OUT.parent)}})
client.execute()
nbf.write(nb, OUT)
print("executed OK")
