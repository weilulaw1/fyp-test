import json
import sys
import os
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Threshold: max classes per diagram before splitting
MAX_CLASSES = 200
MAX_DEPTH = 3  # Optional depth limit

# Global stores
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
    return str(name).replace("/", "_").replace(".", "_").replace(" ", "_").replace("-", "_")


def add_class(name, attributes):
    """Register a PlantUML class with given attributes."""
    safe = sanitize(name)
    if safe not in classes:
        classes[safe] = set()
    for attr, atype in attributes.items():
        classes[safe].add(f"{attr}: {atype}")


def add_class_from_path(path, summary, functions):
    """Create a class from a file path and its functions."""
    class_name = sanitize(Path(path).stem)
    attrs = {"summary": "string"}
    add_class(class_name, attrs)

    for func in functions or []:
        if isinstance(func, dict) and "name" in func:
            func_name = sanitize(func["name"])
            classes[class_name].add(f"{func_name}()")
        elif isinstance(func, str):
            classes[class_name].add(f"{sanitize(func)}()")


def reset_globals():
    """Clear classes and relationships before generating a new diagram."""
    global classes, relationships
    classes = {}
    relationships = []


def flush_diagram(filename_suffix):
    """Write current UML part to file."""
    global file_path, base_name, part_index, OUTPUT_DIR

    filename = f"{base_name}{filename_suffix}"
    uml_lines = ["@startuml"]

    MAX_ITEMS_PER_CLASS = 10
    for cls, attrs in classes.items():
        uml_lines.append(f"class {cls} {{")
        attrs_list = sorted(list(attrs))
        if len(attrs_list) > MAX_ITEMS_PER_CLASS:
            visible_attrs = attrs_list[:MAX_ITEMS_PER_CLASS]
            remaining = len(attrs_list) - MAX_ITEMS_PER_CLASS
            for attr in visible_attrs:
                uml_lines.append(f"  {attr}")
            uml_lines.append(f"  // ... ({remaining} more not shown)")
        else:
            for attr in attrs_list:
                uml_lines.append(f"  {attr}")
        uml_lines.append("}")

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
    global classes, relationships, file_path, base_name

    if depth > MAX_DEPTH:
        return

    if isinstance(node, dict):
        if "path" in node:
            add_class_from_path(node["path"], node.get("summary", ""), node.get("functions", []))
            if parent_name:
                relationships.append((parent_name, Path(node["path"]).stem))
        else:
            name = node.get("name", "Unnamed")
            safe_name = sanitize(name)
            attributes = {k: type(v).__name__ for k, v in node.items() if not isinstance(v, (dict, list))}
            add_class(safe_name, attributes)
            if parent_name:
                relationships.append((parent_name, safe_name))

        if len(classes) >= MAX_CLASSES:
            flush_diagram(f"_part{part_index}.txt")
            reset_globals()

        current_parent = sanitize(node.get("name") or (Path(node["path"]).stem if "path" in node else None))
        for key in ["children", "files"]:
            if key in node:
                for child in node[key]:
                    process_node(child, parent_name=current_parent, depth=depth + 1)

        if "functions" in node and "path" not in node:
            for func in node["functions"]:
                if isinstance(func, dict) and "name" in func:
                    classes[sanitize(node.get("name", "Unnamed"))].add(f"{sanitize(func['name'])}()")
                elif isinstance(func, str):
                    classes[sanitize(node.get("name", "Unnamed"))].add(f"{sanitize(func)}()")

    elif isinstance(node, list):
        for item in node:
            process_node(item, parent_name, depth)


def count_nodes(node):
    if isinstance(node, dict):
        total = 1
        for key in ["children", "files", "functions"]:
            if key in node:
                for child in node[key]:
                    total += count_nodes(child)
        return total
    elif isinstance(node, list):
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

    if total_nodes <= MAX_CLASSES or "children" not in data:
        print("Generating single UML diagram...")
        reset_globals()
        process_node(data)
        flush_diagram(".txt")
    else:
        print("JSON too big, splitting into multiple diagrams...")
        reset_globals()
        root_name = sanitize(data.get("name", "Root"))
        add_class(root_name, {"name": "str"})
        if "children" in data:
            for child in data["children"]:
                child_name = sanitize(child.get("name", "Child"))
                add_class(child_name, {"name": "str"})
                relationships.append((root_name, child_name))
        flush_diagram("_overview.txt")

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
