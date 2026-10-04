"""Execute ML-08 using this Python environment and validate all saved outputs."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from jupyter_client import AsyncKernelManager
from jupyter_client.kernelspec import KernelSpecManager
import nbformat
from nbclient import NotebookClient


def main():
    root = Path(__file__).resolve().parents[2]
    notebook_path = root / "work/notebooks/w05_model.ipynb"
    notebook = nbformat.read(notebook_path, as_version=4)
    with TemporaryDirectory(prefix="flyrank-ml08-") as kernel_dir:
        spec_dir = Path(kernel_dir) / "python3"
        spec_dir.mkdir()
        (spec_dir / "kernel.json").write_text(json.dumps({
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "Python 3", "language": "python",
        }))
        class LocalKernelManager(AsyncKernelManager):
            def __init__(self, **kwargs):
                kwargs["kernel_spec_manager"] = KernelSpecManager(kernel_dirs=[kernel_dir])
                super().__init__(**kwargs)

        NotebookClient(
            notebook, kernel_name="python3", kernel_manager_class=LocalKernelManager,
            timeout=300, resources={"metadata": {"path": str(root)}},
        ).execute()
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    assert all(cell.execution_count is not None for cell in code_cells)
    assert not any(output.output_type == "error"
                   for cell in code_cells for output in cell.outputs)
    nbformat.validate(notebook)
    nbformat.write(notebook, notebook_path)
    print(f"PASS: executed and saved {len(code_cells)} code cells: {notebook_path}")


if __name__ == "__main__":
    main()
