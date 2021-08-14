#!/usr/bin/env python
import argparse
import json
import typing
from io import StringIO


parser = argparse.ArgumentParser(
    description="Generate the Plox AST representation from a JSON data file."
)
parser.add_argument("ast_data", help="File path of the JSON data file.", type=str)
parser.add_argument(
    "--output",
    "-o",
    help="File path to write the generated python file to.",
    type=str,
    default=None,
)

args = parser.parse_args()


with open(args.ast_data, "r") as data_file:
    ast_data = json.load(data_file)


ast_classes = set(ast_data.keys())
ast_classes.add("Expr")

attribute_types = set(
    [
        attribute_data["type"]
        for attributes in ast_data.values()
        for attribute_data in attributes.values()
    ]
)

source = StringIO()

source.write("from abc import ABC, abstractmethod\n")
if attribute_types - ast_classes:
    python_types = [
        type for type in attribute_types - ast_classes if getattr(typing, type, False)
    ]
    source.write(f"from typing import {', '.join(python_types)}\n")
    source.write("\n")

source.write("from attr import define\n")
source.write("\n")
source.write("from plox.tokens import Token\n")
source.write("\n")
source.write("\n")

source.write("class Expr:\n")
source.write('    def accept(self, visitor: "AstVisitor"):\n')
source.write("        ...\n")

for class_name, attributes in ast_data.items():
    source.write("\n")
    source.write("\n")
    source.write("@define\n")
    source.write(f"class {class_name}(Expr):\n")

    for attribute_name, attribute_data in attributes.items():
        source.write(f"    {attribute_name}: {attribute_data['type']}\n")

    source.write("\n")
    source.write('    def accept(self, visitor: "AstVisitor"):\n')
    source.write(f"        return visitor.visit_{class_name.lower()}(self)\n")

source.write("\n")
source.write("\n")
source.write("class AstVisitor(ABC):\n")
for class_name in ast_data.keys():
    source.write("    @abstractmethod\n")
    source.write(
        f"    def visit_{class_name.lower()}(self, expr: {class_name}):\n"
    )
    source.write("        ...\n")
    source.write("\n")


if args.output:
    with open(args.output, "w") as output_file:
        output_file.write(source.getvalue())

else:
    print(source.getvalue())
