import json
import sys
import os
import io
from pathlib import Path
import textwrap
import hashlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# --- Configuration ---
MAX_CLASSES = 40          # hard cap per diagram (keeps PlantUML stable)
MAX_DEPTH = 3
SUMMARY_WRAP_WIDTH = 40
MAX_METHODS_SHOWN = 12

# Global stores
classes = {}        # { class_id: {"name": str, "attrs": set[str], "summary": str} }
relationships = []  # list[(parent_id, child_id)]

OUTPUT_DIR = None
base_name = None
part_index = 1


def safe_text(s: object) -> str:
    """Make text safer for PlantUML rendering."""
    if s is None:
        return ""
    return (
        str(s)
        .replace('"', "'")
        .replace("{", "(")
        .replace("}", ")")
    )


def sanitize_id(raw: object) -> str:
    """
    Creates a stable, collision-safe PlantUML ID:
    - readable base made of alnum/_ only
    - short md5 suffix to avoid collisions
    """
    if not raw:
        raw = "Unnamed"
    s = str(raw)
    base = "".join(c if c.isalnum() else "_" for c in s)
    h = hashlib.md5(s.encode("utf-8")).hexdigest()[:8]
    return f"{base}_{h}"


SKIP_KEYS = {"summary", "children", "files", "functions", "path", "name"}


def register_class(node_id: str, display_name: str, summary: str = "", attributes=None):
    """Ensure a class exists; don't overwrite summary if already set."""
    if node_id not in classes:
        classes[node_id] = {
            "name": safe_text(display_name),
            "attrs": set(),
            "summary": safe_text(summary),
        }
    else:
        # keep the first non-empty summary we saw (avoids oscillation)
        if summary and not classes[node_id]["summary"]:
            classes[node_id]["summary"] = safe_text(summary)

    if attributes:
        for k, v in attributes.items():
            if k in SKIP_KEYS:
                continue
            if isinstance(v, (dict, list)):
                continue
            classes[node_id]["attrs"].add(f"{safe_text(k)}: {safe_text(v)}")


def reset_globals():
    global classes, relationships
    classes = {}
    relationships = []


def flush_diagram(filename_suffix: str, title: str = "Diagram"):
    global part_index, base_name, OUTPUT_DIR

    filename = f"{base_name}{filename_suffix}"

    uml_lines = [
        "@startuml",
        "skinparam monochrome true",
        "top to bottom direction",
        "skinparam linetype ortho",
        "skinparam classAttributeIconSize 0",
        "skinparam noteFontSize 11",
        "skinparam noteBackgroundColor #f9f9f9",
    ]
    uml_lines.append(f"title {safe_text(title)} - Part {part_index}")

    # 1) Classes + their attributes (limited)
    for cid, data in classes.items():
        uml_lines.append(f'class "{data["name"]}" as {cid} {{')

        sorted_attrs = sorted(list(data["attrs"]))
        visible = sorted_attrs[:MAX_METHODS_SHOWN]
        for attr in visible:
            uml_lines.append(f"  {attr}")

        if len(sorted_attrs) > MAX_METHODS_SHOWN:
            uml_lines.append(f"  ... ({len(sorted_attrs) - MAX_METHODS_SHOWN} more)")

        uml_lines.append("}")

        # 2) Summary note (wrapped, outside the class)
        if data["summary"]:
            wrapped_lines = textwrap.wrap(data["summary"], width=SUMMARY_WRAP_WIDTH)
            uml_lines.append(f"note bottom of {cid}")
            for line in wrapped_lines:
                uml_lines.append(f"  {line}")
            uml_lines.append("end note")

    # 3) Relationships (only if both endpoints exist in this part)
    for parent, child in set(relationships):
        if parent in classes and child in classes:
            uml_lines.append(f"{parent} --> {child}")

    uml_lines.append("@enduml")

    out = OUTPUT_DIR / filename
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(uml_lines))

    print(f"[OK] Saved: {out}")
    part_index += 1


def process_node(node: dict, parent_id: str | None = None, depth: int = 0):
    if depth > MAX_DEPTH:
        return

    # hard cap for stability
    if len(classes) >= MAX_CLASSES:
        return

    # Determine display name + stable ID
    name = node.get("name") or (Path(node["path"]).stem if "path" in node else "Unnamed")
    node_id = sanitize_id(node.get("path") or name)  # path is a better unique basis

    # Register class (skip path/name so boxes don't get huge)
    register_class(node_id, name, summary=node.get("summary", ""), attributes=node)

    # Add functions as methods
    for func in node.get("functions", []) or []:
        func_name = func.get("name") if isinstance(func, dict) else str(func)
        func_name = safe_text(func_name)
        if func_name:
            classes[node_id]["attrs"].add(f"{func_name}()")

    # Link to parent
    if parent_id:
        relationships.append((parent_id, node_id))

    # Recurse
    for key in ["children", "files"]:
        for child in node.get(key, []) or []:
            if isinstance(child, dict):
                process_node(child, parent_id=node_id, depth=depth + 1)


def main(fp: str, out_path: str):
    global base_name, OUTPUT_DIR, part_index

    file_path = Path(fp)
    base_name = file_path.stem
    OUTPUT_DIR = Path(out_path)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    part_index = 1

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # Split by top-level children if present
    if isinstance(data, dict) and data.get("children"):
        # 1) Overview diagram
        reset_globals()
        root_name = data.get("name", "Root")
        root_id = sanitize_id(root_name)
        register_class(root_id, root_name, summary=data.get("summary", ""))

        for child in data["children"]:
            if not isinstance(child, dict):
                continue
            c_name = child.get("name") or (Path(child["path"]).stem if "path" in child else "Module")
            c_id = sanitize_id(child.get("path") or c_name)
            register_class(c_id, c_name)
            relationships.append((root_id, c_id))

        flush_diagram("_overview.txt", title="Project Overview")

        # 2) One detailed diagram per top-level child
        for child in data["children"]:
            if not isinstance(child, dict):
                continue
            reset_globals()

            # re-add root so child isn't orphaned
            register_class(root_id, root_name)

            process_node(child, parent_id=root_id)

            child_label = child.get("name") or (Path(child["path"]).stem if "path" in child else "Module")
            flush_diagram(f"_{sanitize_id(child_label)}.txt", title=f"Module: {child_label}")

    else:
        # Single diagram for smaller JSON
        reset_globals()
        if isinstance(data, dict):
            process_node(data)
        flush_diagram(".txt", title="System Architecture")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python json_to_uml.py <input.json> <output_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
