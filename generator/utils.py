import json
import os
import re
from enum import Enum
from os import path
from pathlib import Path
from typing import Dict

import black
import yaml
from stringcase import camelcase


def uppercamelcase(string):
    return (string[0].upper() + camelcase(string[1:])) if string else None


class PythonVersion(Enum):
    PY_36 = "3.6"
    PY_37 = "3.7"
    PY_38 = "3.8"


BLACK_PYTHON_VERSION: Dict[PythonVersion, black.TargetVersion] = {
    PythonVersion.PY_36: black.TargetVersion.PY36,
    PythonVersion.PY_37: black.TargetVersion.PY37,
    PythonVersion.PY_38: black.TargetVersion.PY38,
}


black_mode = black.FileMode(
    target_versions={BLACK_PYTHON_VERSION[PythonVersion["PY_36"]]},
    line_length=black.DEFAULT_LINE_LENGTH,
    string_normalization=False,
)


def clean_json(string):
    string = re.sub(",[ \t\r\n]+}", "}", string)
    string = re.sub(",[ \t\r\n]+\]", "]", string)

    return string


def split_add_content_escape(contents):
    return {
        key: content.replace('"', '\\"').split("\n")
        for key, content in contents.items()
    }


def make_package(name, directory, init_code=None, force_dir=False):
    path = make_directory(name=name, directory=directory, force_dir=force_dir)
    with open(f"{path}/__init__.py", "w+") as f:
        if init_code:
            f.write(init_code)
        return path


def make_directory(name, directory, force_dir=False):
    final_path = f"{directory}/{name}"
    if not path.exists(directory):
        if force_dir:
            Path(directory).mkdir(parents=True, exist_ok=True)
        else:
            raise FileExistsError(f"Directory { directory } doesn't exist")
    os.mkdir(final_path)
    return final_path


def make_file(name, directory, code=None, force_dir=False):
    final_path = f"{directory}/{name}"
    if not path.exists(directory):
        if force_dir:
            Path(directory).mkdir(parents=True, exist_ok=True)
        else:
            raise FileExistsError(f"Directory { directory } doesn't exist")
    with open(final_path, "w+") as f:
        if code:
            f.write(code)
        return final_path


def read_spec(service_file):
    with open(service_file, "r") as stream:
        return yaml.safe_load(stream)


def read_json(file):
    with open(file, "r") as stream:
        json_data = clean_json(stream.read())
        return json.loads(json_data)
