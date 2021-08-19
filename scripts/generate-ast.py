#!/usr/bin/env python
import argparse
import json
import typing
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


classes = set(class_spec["children"].keys())
classes.add(class_spec["parent"])

attribute_types = set(
    [
        type
        for attributes in class_spec["children"].values()
        for type in attributes.values()
    ]
)

import_lines = [
    "from abc import ABC, abstractmethod",
    "",
    "from attr import define",
    "",
    "from plox.tokens import Token",
]
if attribute_types - classes:
    python_types = [
        type for type in attribute_types - classes if getattr(typing, type, False)
    ]
    import_lines.insert(1, f"from typing import {', '.join(python_types)}")
import_block = "\n".join(import_lines)

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
