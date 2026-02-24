import json
import sys
import os
import io
from pathlib import Path
import textwrap

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Threshold: max classes per diagram before splitting
MAX_CLASSES = 200
MAX_DEPTH = 3  # Optional depth limit

# Summary-as-comments formatting (inside class)
SUMMARY_WRAP_WIDTH = 42
SUMMARY_MAX_LINES = None  # set to an int (e.g., 8) to cap summary height
SUMMARY_CLIP_CHARS = 2000  # safety cap so notes don't explode

# Global stores
# classes: { class_name: set(lines) }
classes = {}
relationships = []

# Globals set in main()
file_path = None
base_name = None
part_index = 1
OUTPUT_DIR = None


def sanitize(name):
    """Make a safe class name for PlantUML (consistent)."""
    if name is None:
        return "Unnamed"
    return (
        str(name)
        .replace("/", "_")
        .replace(".", "_")
        .replace(" ", "_")
        .replace("-", "_")
    )


def add_class(name, attributes):
    """Register a PlantUML class with given attributes."""
    safe = sanitize(name)
    if safe not in classes:
        classes[safe] = set()
    for attr, val in attributes.items():
        classes[safe].add(f"{attr}: {val}")


def add_summary_as_comments(class_name, summary):
    if not isinstance(summary, str) or not summary.strip():
        return

    safe = sanitize(class_name)
    classes.setdefault(safe, set())

    text = summary.strip().replace("\r", "")
    if len(text) > SUMMARY_CLIP_CHARS:
        text = text[:SUMMARY_CLIP_CHARS] + "..."

    wrapped = textwrap.wrap(text, width=SUMMARY_WRAP_WIDTH)

    # Header
    classes[safe].add("__SUMMARY__0000Summary:")
    classes[safe].add("__SUMMARY__0001--")

    # Body
    for i, line in enumerate(wrapped):
        classes[safe].add(f"__SUMMARY__{i + 2:04d}{line}")

    # Divider AFTER all summary lines
    end_index = len(wrapped) + 2
    classes[safe].add(
        f"__SUMMARY__{end_index:04d}{'--'}"
    )


def add_class_from_path(path, summary, functions):
    """Create a class from a file path and its functions."""
    class_name = sanitize(Path(path).stem)

    # Keep your original marker attribute (optional)
    add_class(class_name, {"summary": "string"})

    # Put the actual summary inside the class (comments)
    add_summary_as_comments(class_name, summary)

    # Methods
    for func in functions or []:
        if isinstance(func, dict) and "name" in func:
            func_name = sanitize(func["name"])
            classes[class_name].add(f"{func_name}()")
        elif isinstance(func, str):
            classes[class_name].add(f"{sanitize(func)}()")


def reset_globals():
    """Clear classes/relationships before generating a new diagram."""
    global classes, relationships
    classes = {}
    relationships = []


def flush_diagram(filename_suffix):
    """Write current UML part to file."""
    global base_name, part_index, OUTPUT_DIR

    filename = f"{base_name}{filename_suffix}"
    uml_lines = ["@startuml"]

    MAX_ITEMS_PER_CLASS = 10
    for cls, attrs in classes.items():
        uml_lines.append(f"class {cls} {{")

        summary_lines = sorted([a for a in attrs if a.startswith("__SUMMARY__")])
        other_lines = sorted([a for a in attrs if not a.startswith("__SUMMARY__")])

        # Print ALL summary lines (remove marker)
        for line in summary_lines:
            uml_lines.append(f"  {line[len('__SUMMARY__') + 4:]}")


        # Print limited non-summary lines
        if len(other_lines) > MAX_ITEMS_PER_CLASS:
            visible = other_lines[:MAX_ITEMS_PER_CLASS]
            remaining = len(other_lines) - MAX_ITEMS_PER_CLASS
            for line in visible:
                uml_lines.append(f"  {line}")
            uml_lines.append(f"  // ... ({remaining} more not shown)")
        else:
            for line in other_lines:
                uml_lines.append(f"  {line}")

        uml_lines.append("}")


    # Relationships
    for rel in relationships:
        if isinstance(rel, tuple):
            a, b = rel
            uml_lines.append(f"{sanitize(a)} --> {sanitize(b)}")
        else:
            uml_lines.append(rel)

    uml_lines.append("@enduml")

    out = OUTPUT_DIR / filename
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(uml_lines))

    print(f"[OK] UML written to {out} (part {part_index})")
    part_index += 1


def process_node(node, parent_name=None, depth=0):
    global relationships

    if depth > MAX_DEPTH:
        return

    if isinstance(node, dict):
        # File node (your JSON format: has "path")
        if "path" in node:
            add_class_from_path(
                node["path"],
                node.get("summary", ""),
                node.get("functions", []),
            )
            if parent_name:
                relationships.append((parent_name, Path(node["path"]).stem))

        # General node (project/module/etc.)
        else:
            name = node.get("name", "Unnamed")
            safe_name = sanitize(name)

            # Keep attributes small + human-readable (not type names)
            attributes = {}
            for k, v in node.items():
                if isinstance(v, (dict, list)):
                    continue
                if k == "summary":
                    continue  # summary goes inside class as comments
                attributes[k] = str(v)

            # Always add something so the class isn't empty (optional)
            if not attributes:
                attributes = {"name": "string"}

            add_class(safe_name, attributes)

            # Put summary inside class
            add_summary_as_comments(safe_name, node.get("summary", ""))

            if parent_name:
                relationships.append((parent_name, safe_name))

        # Split if too many classes
        if len(classes) >= MAX_CLASSES:
            flush_diagram(f"_part{part_index}.txt")
            reset_globals()

        # Recurse into children/files
        current_parent = sanitize(
            node.get("name") or (Path(node["path"]).stem if "path" in node else None)
        )
        for key in ["children", "files"]:
            if key in node and isinstance(node[key], list):
                for child in node[key]:
                    process_node(child, parent_name=current_parent, depth=depth + 1)

        # Attach functions to non-path nodes as methods
        if "functions" in node and "path" not in node:
            owner = sanitize(node.get("name", "Unnamed"))
            for func in node["functions"] or []:
                if isinstance(func, dict) and "name" in func:
                    classes.setdefault(owner, set()).add(f"{sanitize(func['name'])}()")
                elif isinstance(func, str):
                    classes.setdefault(owner, set()).add(f"{sanitize(func)}()")

    elif isinstance(node, list):
        for item in node:
            process_node(item, parent_name, depth)


def count_nodes(node):
    if isinstance(node, dict):
        total = 1
        for key in ["children", "files", "functions"]:
            if key in node and isinstance(node[key], list):
                for child in node[key]:
                    total += count_nodes(child)
        return total
    if isinstance(node, list):
        return sum(count_nodes(n) for n in node)
    return 0


def main(fp, output_dir):
    global file_path, base_name, part_index, OUTPUT_DIR

    file_path = fp
    base_name = Path(file_path).stem
    part_index = 1

    OUTPUT_DIR = Path(output_dir)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    total_nodes = count_nodes(data)
    print(f"Total nodes in JSON: {total_nodes}")

    if total_nodes <= MAX_CLASSES or not (isinstance(data, dict) and "children" in data):
        print("Generating single UML diagram...")
        reset_globals()
        process_node(data)
        flush_diagram(".txt")
    else:
        print("JSON too big, splitting into multiple diagrams...")

        # Overview
        reset_globals()
        root_name = sanitize(data.get("name", "Root"))
        add_class(root_name, {"name": "str"})

        # Root summary inside class (comments)
        add_summary_as_comments(root_name, data.get("summary", ""))

        if "children" in data:
            for child in data["children"]:
                child_name = sanitize(child.get("name", "Child"))
                add_class(child_name, {"name": "str"})
                relationships.append((root_name, child_name))

        flush_diagram("_overview.txt")

        # One diagram per child
        for child in data.get("children", []):
            reset_globals()
            process_node(child, parent_name=root_name)
            flush_diagram(f"_{sanitize(child.get('name','Child'))}.txt")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python json_to_uml.py <file.json> <output_dir>")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2]
    main(file_path, output_dir)
