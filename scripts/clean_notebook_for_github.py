#!/usr/bin/env python3
import json
import sys
from pathlib import Path


WIDGET_VIEW_MIME = "application/vnd.jupyter.widget-view+json"


def clean_notebook(path: Path) -> bool:
    changed = False
    with path.open() as f:
        nb = json.load(f)

    metadata = nb.get("metadata", {})
    widgets_meta = metadata.get("widgets")
    if isinstance(widgets_meta, dict) and "state" not in widgets_meta:
        del metadata["widgets"]
        changed = True

    for cell in nb.get("cells", []):
        outputs = cell.get("outputs")
        if not isinstance(outputs, list):
            continue

        filtered_outputs = []
        for output in outputs:
            data = output.get("data")
            if isinstance(data, dict) and WIDGET_VIEW_MIME in data:
                changed = True
                continue
            filtered_outputs.append(output)

        if len(filtered_outputs) != len(outputs):
            cell["outputs"] = filtered_outputs

    if changed:
        with path.open("w") as f:
            json.dump(nb, f, indent=2)
            f.write("\n")

    return changed


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: clean_notebook_for_github.py <notebook.ipynb>", file=sys.stderr)
        return 2

    notebook_path = Path(sys.argv[1]).resolve()
    if not notebook_path.exists():
        print(f"Notebook not found: {notebook_path}", file=sys.stderr)
        return 1

    changed = clean_notebook(notebook_path)
    print(f"{'Updated' if changed else 'No changes needed'}: {notebook_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
