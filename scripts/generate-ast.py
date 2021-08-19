#!/usr/bin/env python
import argparse
import json
import typing
from collections import defaultdict
from io import StringIO
from typing import Dict, List


parser = argparse.ArgumentParser(
    description="Generate a Plox data class structure from a JSON data file."
)
parser.add_argument("class_spec", help="File path of the JSON data file.", type=str)
parser.add_argument(
    "--output",
    "-o",
    help="File path to write the generated python file to.",
    type=str,
    default=None,
)

args = parser.parse_args()


with open(args.class_spec, "r") as data_file:
    class_spec = json.load(data_file)


extra_imports = defaultdict(set)
for child, attributes in class_spec["children"].items():
    for attr_name, type_name in attributes.items():
        if "." in type_name:
            import_class = type_name.split(".")[-1]
            import_path = ".".join(type_name.split(".")[:-1])
            extra_imports[import_path].add(import_class)
            attributes[attr_name] = import_class

stdlib_imports = [
    "from abc import ABC, abstractmethod",
]
external_imports = [
    "from attr import define",
]
plox_imports = [
    "from plox.tokens import Token",
]

for path, names in extra_imports.items():
    if "plox" in path:
        plox_imports.append(f"from {path} import {','.join(names)}")
    else:
        stdlib_imports.insert(1, f"from {path} import {','.join(names)}")

import_block = "\n\n".join(
    [
        "\n".join(stdlib_imports),
        "\n".join(external_imports),
        "\n".join(sorted(plox_imports)),
    ]
)

parent_block = f"""class {class_spec["parent"]}:
    def accept(self, visitor: "{class_spec["parent"]}Visitor"):
        ..."""


def generate_child_definition(child_name: str, attributes: List[Dict[str, str]]) -> str:
    definition_lines = ["@define", f"class {child_name}({class_spec['parent']}):"]
    definition_lines.extend(
        [f"    {name}: {type}" for name, type in attributes.items()]
    )
    definition_lines.append("")
    definition_lines.extend(
        [
            f'    def accept(self, visitor: "{class_spec["parent"]}Visitor"):',
            f"        return visitor.visit_{child_name.lower()}(self)",
        ]
    )
    return "\n".join(definition_lines)


visitor_lines = [f"class {class_spec['parent']}Visitor(ABC):"]
for child in class_spec["children"].keys():
    visitor_lines.extend(
        [
            "    @abstractmethod",
            f"    def visit_{child.lower()}(self, expr: {child}):",
            "        ...",
            "",
        ]
    )
visitor_block = "\n".join(visitor_lines)

source_blocks = [import_block, parent_block]
source_blocks.extend(
    [
        generate_child_definition(child, attributes)
        for child, attributes in class_spec["children"].items()
    ]
)
source_blocks.append(visitor_block)

source = "\n\n\n".join(source_blocks)

if args.output:
    with open(args.output, "w") as output_file:
        output_file.write(source)

else:
    print(source)
