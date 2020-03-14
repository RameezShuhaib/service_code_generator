from typing import Dict
from generator.utils import make_directory, make_file, make_package
from generator.components import make


def generate_template(data: Dict, current_dir: str):
    code = make(template_name=data["template"], variables=data.get("variables"))
    make_file(name=data["name"], directory=current_dir, code=code)


def generate_data(data: Dict, current_dir: str):
    make_file(name=data["name"], directory=current_dir, code=data["data"])


def generate_modules(data: Dict, current_dir: str = "."):

    if data["type"] == "DIRECTORY":
        next_dir = make_directory(name=data["name"], directory=current_dir)
        for module in data["sub"]:
            generate_modules(data=module, current_dir=next_dir)

    if data["type"] == "PACKAGE":
        next_dir = make_package(
            name=data["name"], init_code=data.get("init_code"), directory=current_dir
        )
        for module in data["sub"]:
            generate_modules(data=module, current_dir=next_dir)

    elif data["type"] == "TEMPLATE":
        generate_template(data, current_dir)

    elif data["type"] == "DATA":
        generate_data(data, current_dir)
