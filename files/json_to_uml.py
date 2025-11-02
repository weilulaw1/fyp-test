import json
import sys
import io
from pathlib import Path


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# Threshold: max classes per diagram before splitting
MAX_CLASSES = 200
# Optional depth limit to keep diagrams readable
MAX_DEPTH = 3

# Global store for classes and relationships
classes = {}
relationships = []

# Globals to be set in main()
file_path = None
base_name = None
part_index = 1


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
    # Use filename as class name (sanitized)
    class_name = sanitize(Path(path).stem)
    attrs = {}
    if summary:
        attrs["summary"] = "string"
    else:
        attrs["summary"] = "string"  # keep attribute so class is non-empty
    add_class(class_name, attrs)

    # Add functions as methods (stored as attributes with () so PlantUML shows them)
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
    """Write current classes+relationships into a puml/txt file and keep counting parts."""
    global file_path, base_name, part_index
    if file_path is None or base_name is None:
        raise RuntimeError("file_path and base_name must be set before flushing diagrams.")

    filename = f"{base_name}{filename_suffix}"
    uml_lines = ["@startuml"]

    MAX_ITEMS_PER_CLASS = 10  # <-- Limit attributes/methods per class

    for cls, attrs in classes.items():
        uml_lines.append(f"class {cls} {{")
        attrs_list = sorted(list(attrs))  # keep consistent order

        # If too many attributes/methods, show only first N
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

    # write relationships sanitized
    for rel in relationships:
        if isinstance(rel, tuple):
            a, b = rel
            uml_lines.append(f"{sanitize(a)} --> {sanitize(b)}")
        else:
            if "-->" in rel:
                left, right = rel.split("-->")
                uml_lines.append(f"{sanitize(left.strip())} --> {sanitize(right.strip())}")
            else:
                uml_lines.append(rel)

    uml_lines.append("@enduml")

    out = Path(file_path).parent / filename
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(uml_lines))
    print(f"✅ UML written to {out} (part {part_index})")
    part_index += 1


def process_node(node, parent_name=None, depth=0):
    """
    Recursively process JSON nodes into PlantUML classes + relationships.
    This will flush to a new part file when classes exceed MAX_CLASSES.
    """
    global classes, relationships, file_path, base_name

    if depth > MAX_DEPTH:
        return

    if isinstance(node, dict):
        # If this node has a 'path', treat it as a file-based class
        if "path" in node:
            add_class_from_path(
                node["path"],
                node.get("summary", ""),
                node.get("functions", [])
            )
            # If there is a parent, link the parent's sanitized name to this file-class
            if parent_name:
                relationships.append((parent_name, Path(node["path"]).stem))
        else:
            # Otherwise, use standard name-based processing
            name = node.get("name", "Unnamed")
            safe_name = sanitize(name)

            # Collect scalar attributes only
            attributes = {}
            for key, value in node.items():
                if isinstance(value, (dict, list)):
                    continue
                # keep minimal info (type) to avoid huge summaries
                attributes[key] = type(value).__name__
            add_class(safe_name, attributes)

            # Add relationship to parent (store as tuple to sanitize later)
            if parent_name:
                relationships.append((parent_name, safe_name))

        # If diagram is getting large, flush current part and reset, but keep the current node processing
        if len(classes) >= MAX_CLASSES:
            # flush with suffix indicating a part
            flush_diagram(f"_part{part_index}.txt")
            reset_globals()

        # Recurse into children and files (use node's sanitized name as parent)
        current_parent = sanitize(node.get("name") or (Path(node["path"]).stem if "path" in node else None))
        for key in ["children", "files"]:
            if key in node:
                for child in node[key]:
                    process_node(child, parent_name=current_parent, depth=depth + 1)

        # functions usually processed as part of path nodes; if functions exist on non-path nodes,
        # add them as pseudo-methods to the node's class
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
    """Count total number of nodes (classes) in JSON."""
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


def main(fp):
    global file_path, base_name, part_index
    file_path = fp
    base_name = Path(file_path).stem
    part_index = 1

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    total_nodes = count_nodes(data)
    print(f"Total nodes in JSON: {total_nodes}")

    # If small, generate single UML; else generate overview + parts
    if total_nodes <= MAX_CLASSES or "children" not in data:
        print("Generating single UML diagram...")
        reset_globals()
        process_node(data)
        flush_diagram(".txt")
    else:
        print("JSON too big, splitting into multiple diagrams...")
        # overview: show root -> top-level children (sanitized)
        reset_globals()
        root_name = sanitize(data.get("name", "Root"))
        add_class(root_name, {"name": "str"})
        if "children" in data:
            for child in data["children"]:
                child_name = sanitize(child.get("name", "Child"))
                add_class(child_name, {"name": "str"})
                relationships.append((root_name, child_name))
        flush_diagram("_overview.txt")

        # generate one diagram per child (but each child run may itself flush into multiple parts)
        if "children" in data:
            for child in data["children"]:
                reset_globals()
                process_node(child, parent_name=root_name)
                # after processing the child subtree, flush current accumulated diagram (could be empty)
                flush_diagram(f"_{sanitize(child.get('name','Child'))}.txt")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python json_to_uml.py <file.json>")
        sys.exit(1)
    main(sys.argv[1])
