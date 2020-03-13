import json
import os
from os import path
from pathlib import Path

import yaml
from jsoncomment import JsonComment


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


def read_service_spec(service_file):
    with open(service_file, "r") as stream:
        return yaml.safe_load(stream)


def read_json(file):
    with open(file, "r") as stream:
        parser = JsonComment(stream.read())
        return json.loads(parser)
