import json
import sys
from pathlib import Path

# Threshold: max classes per diagram before splitting
MAX_CLASSES = 500
# Optional depth limit to keep diagrams readable
MAX_DEPTH = 3

# Global store for classes and relationships
classes = {}
relationships = []

def add_class(name, attributes):
    """Register a PlantUML class with given attributes."""
    if name not in classes:
        classes[name] = set()
    for attr, atype in attributes.items():
        classes[name].add(f"{attr}: {atype}")

def process_node(node, parent_name=None, depth=0):
    """Recursively process JSON nodes into PlantUML classes + relationships."""
    if depth > MAX_DEPTH:
        return

    if isinstance(node, dict):
        # Determine class name
        name = node.get("name", "Unnamed").replace(" ", "_")
        if not name:
            name = "Node"

        # Collect attributes (skip nested dict/list)
        attributes = {}
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                continue
            attributes[key] = type(value).__name__
        add_class(name, attributes)

        # Add relationship to parent
        if parent_name:
            relationships.append(f"{parent_name} --> {name}")

        # Recurse into children, files, functions
        for key in ["children", "files", "functions"]:
            if key in node:
                for child in node[key]:
                    process_node(child, name, depth + 1)

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

def write_uml(file_path, filename):
    """Write collected classes and relationships to a .txt file."""
    uml_lines = ["@startuml"]
    for cls, attrs in classes.items():
        uml_lines.append(f"class {cls} {{")
        for attr in attrs:
            uml_lines.append(f"  {attr}")
        uml_lines.append("}")
    uml_lines.extend(relationships)
    uml_lines.append("@enduml")

    output_file = Path(file_path).parent / filename
    with open(output_file, "w") as f:
        f.write("\n".join(uml_lines))
    print(f"✅ UML written to {output_file}")

def reset_globals():
    """Clear classes and relationships before generating a new diagram."""
    global classes, relationships
    classes = {}
    relationships = []

def main(file_path):
    with open(file_path) as f:
        data = json.load(f)

    total_nodes = count_nodes(data)
    print(f"Total nodes in JSON: {total_nodes}")

    base_name = Path(file_path).stem

    if total_nodes <= MAX_CLASSES or "children" not in data:
        # Small JSON → generate single UML
        print("Generating single UML diagram...")
        process_node(data)
        write_uml(file_path, f"{base_name}.txt")
    else:
        # Large JSON → split by top-level children
        print("JSON too big, splitting into multiple diagrams...")
        root_name = data.get("name", "Root").replace(" ", "_")

        # Write a top-level overview diagram with only Root and its children
        reset_globals()
        add_class(root_name, {"name": "str"})
        for child in data["children"]:
            child_name = child.get("name", "Child").replace(" ", "_")
            add_class(child_name, {"name": "str"})
            relationships.append(f"{root_name} --> {child_name}")
        write_uml(file_path, f"{base_name}_overview.txt")

        # Generate one diagram per child
        for child in data["children"]:
            reset_globals()
            process_node(child, parent_name=root_name)
            child_safe_name = child.get("name", "Child").replace(" ", "_")
            write_uml(file_path, f"{base_name}_{child_safe_name}.txt")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python json_to_uml.py <file.json>")
        sys.exit(1)
    main(sys.argv[1])
