"""Execute and save the ML-11 capstone with this interpreter's kernel."""
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
    path = root / "work/notebooks/capstone.ipynb"
    notebook = nbformat.read(path, as_version=4)
    with TemporaryDirectory(prefix="flyrank-ml11-") as kernel_dir:
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
            timeout=600, resources={"metadata": {"path": str(root)}},
        ).execute()
    cells = [c for c in notebook.cells if c.cell_type == "code"]
    assert all(c.execution_count is not None for c in cells)
    assert not any(o.output_type == "error" for c in cells for o in c.outputs)
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    print(f"PASS: executed and saved {len(cells)} capstone code cells; prerequisite notebooks and paper regenerated.")


if __name__ == "__main__":
    main()
