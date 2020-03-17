from typing import Dict

import black
from stringcase import snakecase

from generator.components import make_class
from generator.utils import black_mode, uppercamelcase


def _remove_x_keys(data: Dict):
    return {k: data[k] for k in filter(lambda k: k[:2] != "x-", data.keys())}


def _get_fake_class(data: Dict):
    return {
        service_name: {
            "type": "class",
            "name": f"Fake{uppercamelcase(service_name)}",
            "methods": [
                {
                    "name": method_name,
                    "arguments": method["arguments"],
                    "return_type": method["returns"],
                }
                for method_name, method in service.get("interface", {}).items()
            ],
        }
        for service_name, service in data.items()
    }


def make_test_service(service_data: Dict, application):

    service_fakes = _get_fake_class(_remove_x_keys(service_data["x-services"]))
    service_repos = _get_fake_class(_remove_x_keys(service_data["x-repos"]))
    ex_service_repos = _get_fake_class(_remove_x_keys(service_data["x-ex-services"]))

    combined = {**service_fakes, **service_repos, **ex_service_repos}
    fake_dict = {name: make_class(fake).split("\n") for name, fake in combined.items()}

    tests = {
        service_name: {
            "imports": ["import pytest"],
            "type": "class",
            "name": f"Test{uppercamelcase(service_name)}",
            "methods": [
                {
                    "name": f"test_{snakecase(method_name)}",
                    "contents": sum(
                        [
                            fake_dict[dependency["name"]]
                            for dependency in service.get("depends", [])
                        ],
                        [],
                    ),
                }
                for method_name, method in service.get("interface", {}).items()
            ],
        }
        for service_name, service in service_data["x-services"].items()
    }
    return {
        "type": "PACKAGE",
        "name": "services",
        "sub": [
            {
                "type": "DATA",
                "name": f"test_{snakecase(name)}.py",
                "data": black.format_str(make_class(test), mode=black_mode),
            }
            for name, test in tests.items()
        ],
    }
