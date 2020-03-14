import json

from jinja2 import Environment, FileSystemLoader
from stringcase import snakecase

from generator.utils import clean_json


component_loader = FileSystemLoader("generator/components")
env_component = Environment(loader=component_loader)

template_loader = FileSystemLoader("generator/templates")
env_template = Environment(loader=template_loader)


def make_code(statements, imports=()):
    template = env_component.get_template("code")
    return template.render(imports=imports, statements=statements)


def make_class(class_data):
    template = env_component.get_template("class")
    return template.render(class_data=class_data)


def make_api(api_meta, api_data):
    template = env_component.get_template("api")
    structure = []
    for api in api_meta.keys() - ["Spec"]:
        api_json = template.render(
            name=api,
            api_meta=api_meta[api],
            api_data=api_data[snakecase(api)],
            snakecase=snakecase,
        )
        api_json = clean_json(api_json)
        api_class = make_class(json.loads(api_json))

        structure.append(
            {"type": "DATA", "name": f"{snakecase(api)}.py", "data": api_class,}
        )
    return structure


def make_service(service_data):
    template = env_component.get_template("service")
    structure = []
    for service in service_data:
        service_json = template.render(
            name=service, service_data=service_data[service], snakecase=snakecase,
        )
        service_json = clean_json(service_json)
        service_class = make_class(json.loads(service_json))
        structure.append(
            {"type": "DATA", "name": f"{snakecase(service)}.py", "data": service_class,}
        )
    return structure


def make_repo(repo_data):
    template = env_component.get_template("repo")
    structure = []
    for repo in repo_data:
        repo_json = template.render(
            name=repo, repo_data=repo_data[repo], snakecase=snakecase,
        )
        repo_json = clean_json(repo_json)
        repo_class = make_class(json.loads(repo_json))
        structure.append(
            {"type": "DATA", "name": f"{snakecase(repo)}.py", "data": repo_class,}
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
