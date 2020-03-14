import json
from enum import Enum
from typing import Dict

import black
from jinja2 import Environment, FileSystemLoader
from stringcase import snakecase

from generator.utils import clean_json


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


component_loader = FileSystemLoader("generator/components")
env_component = Environment(loader=component_loader)

template_loader = FileSystemLoader("generator/templates")
env_template = Environment(loader=template_loader)


def _filter_type(_type):
    return lambda x: x["type"] == _type


def _get_dependency_types(data):
    repos = list(
        map(lambda x: x["name"], filter(_filter_type("Repo"), data.get("depends", [])))
    )
    services = list(
        map(
            lambda x: x["name"],
            filter(_filter_type("Service"), data.get("depends", [])),
        )
    )
    ex_services = list(
        map(
            lambda x: x["name"],
            filter(_filter_type("ExService"), data.get("depends", [])),
        )
    )
    return repos, services, ex_services


def make_code(statements, imports=()):
    template = env_component.get_template("code")
    return template.render(imports=imports, statements=statements)


def make_class(class_data):
    template = env_component.get_template("class")
    return template.render(class_data=class_data)


def make_api(api_meta, api_data, application):
    template = env_component.get_template("api")
    structure = []
    for api in api_meta.keys() - ["Spec"]:
        repos, services, ex_services = _get_dependency_types(api_meta[api])
        api_json = template.render(
            repos=repos,
            services=services,
            ex_services=ex_services,
            name=api,
            api_meta=api_meta[api],
            api_data=api_data[snakecase(api)],
            snakecase=snakecase,
            application=application,
        )
        api_json = clean_json(api_json)
        api_class = make_class(json.loads(api_json))

        structure.append(
            {
                "type": "DATA",
                "name": f"{snakecase(api)}.py",
                "data": black.format_str(api_class, mode=black_mode),
            }
        )
    return structure


def make_service(service_data, application):
    template = env_component.get_template("service")
    structure = []
    for service in service_data:
        repos, services, ex_services = _get_dependency_types(service_data[service])
        service_json = template.render(
            repos=repos,
            services=services,
            ex_services=ex_services,
            name=service,
            service_data=service_data[service],
            snakecase=snakecase,
            application=application,
        )
        service_json = clean_json(service_json)
        service_class = make_class(json.loads(service_json))
        structure.append(
            {
                "type": "DATA",
                "name": f"{snakecase(service)}.py",
                "data": black.format_str(service_class, mode=black_mode),
            }
        )
    return structure


def make_repo(repo_data, application):
    template = env_component.get_template("repo")
    structure = []
    for repo in repo_data:
        repos, services, ex_services = _get_dependency_types(repo_data[repo])
        repo_json = template.render(
            repos=repos,
            services=services,
            ex_services=ex_services,
            name=repo,
            repo_data=repo_data[repo],
            snakecase=snakecase,
            application=application,
        )
        repo_json = clean_json(repo_json)
        repo_class = make_class(json.loads(repo_json))
        structure.append(
            {
                "type": "DATA",
                "name": f"{snakecase(repo)}.py",
                "data": black.format_str(repo_class, mode=black_mode),
            }
        )
    return structure


def make_method(
    name,
    parameters=None,
    parameter_type_list=None,
    contents=None,
    return_type=None,
    decorators=None,
    is_class=False,
):

    template = env_component.get_template("method")
    return template.render(
        is_class=is_class,
        method_name=name,
        parameters=parameters or [],
        parameter_type_list=parameter_type_list or [],
        return_type=return_type,
        decorators=decorators or [],
        contents=contents,
    )


def make(template_name, variables=None):
    template = env_template.get_template(template_name)
    return template.render(variables=variables)
