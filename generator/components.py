from jinja2 import Environment, FileSystemLoader
from generator.constants import INTEGRATION_TEST_DECORATOR

component_loader = FileSystemLoader("generator/component")
env_component = Environment(loader=component_loader)

template_loader = FileSystemLoader("generator/templates")
env_template = Environment(loader=template_loader)


def make_code(statements, imports=()):
    template = env_component.get_template("code")
    return template.render(imports=imports, statements=statements)


def make_class(class_data):
    template = env_component.get_template("class")
    return template.render(class_data=class_data)


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
