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


def make_service(data):
    template = env_component.get_template("service")
    for service in data["x-services"]:
        service_json = template.render(
            name=service, service_data=data["x-services"][service], snakecase=snakecase,
        )
        service_json = clean_json(service_json)
        service_class = make_class(json.loads(service_json))
        print(service_class)


def make(template_name, variables=None):
    template = env_template.get_template(template_name)
    return template.render(variables=variables)


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
