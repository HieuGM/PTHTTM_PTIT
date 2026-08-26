# -*- coding: utf-8 -*-
"""Build the Ames housing notebook: create .ipynb from source, execute, save with outputs."""
import nbformat as nbf
from nbclient import NotebookClient
import pathlib

SRC = pathlib.Path(r"C:\Users\Laptop\OneDrive\Laptop\Ki 1 - Nam 4\HTTM\assignment01\notebooks\ames_nb_source.py")
OUT = SRC.with_name("02_house_price_system.ipynb")

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.14.6"},
}

lines = SRC.read_text(encoding="utf-8").splitlines()
cells = []
buf_code = []
in_md = False
buf_md = []

def flush_code():
    global buf_code
    if buf_code:
        src = "\n".join(buf_code).strip("\n")
        if src.strip():
            cells.append(nbf.v4.new_code_cell(src))
        buf_code = []

def flush_md():
    global buf_md
    if buf_md:
        src = "\n".join(buf_md).strip("\n")
        if src.strip():
            cells.append(nbf.v4.new_markdown_cell(src))
        buf_md = []

for line in lines:
    if line.startswith("#%% [md]"):
        flush_code()
        flush_md()
        in_md = True
        buf_md = []
    elif line.startswith("#%%"):
        flush_code()
        flush_md()
        in_md = False
        buf_code = []
    else:
        if in_md:
            if line.startswith("#"):
                buf_md.append(line[1:] if line.startswith("# ") else line[1:])
            else:
                buf_md.append(line)
        else:
            buf_code.append(line)
flush_md()
flush_code()
nb.cells = cells
nbf.write(nb, OUT)
print(f"notebook written: {OUT} with {len(cells)} cells")

client = NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(OUT.parent)}})
client.execute()
nbf.write(nb, OUT)
print("executed OK")
