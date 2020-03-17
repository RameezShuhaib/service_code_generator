import json

import black
from jinja2 import Environment, FileSystemLoader
from stringcase import snakecase

from generator.utils import (
    clean_json,
    black_mode,
    uppercamelcase,
    split_add_content_escape,
)


component_loader = FileSystemLoader("generator/components")
env_component = Environment(loader=component_loader)

template_loader = FileSystemLoader("generator/templates")
env_template = Environment(loader=template_loader)


def _filter(a, b):
    return lambda x: x[b] == a


def _get_dependency_types(data):
    repos = list(
        map(
            lambda x: x["name"],
            filter(_filter("Repo", "type"), data.get("depends", [])),
        )
    )
    services = list(
        map(
            lambda x: x["name"],
            filter(_filter("Service", "type"), data.get("depends", [])),
        )
    )
    ex_services = list(
        map(
            lambda x: x["name"],
            filter(_filter("ExService", "type"), data.get("depends", [])),
        )
    )
    return repos, services, ex_services


def make_code(statements, imports=()):
    template = env_component.get_template("code")
    return template.render(imports=imports, statements=statements)


def make_class(class_data):
    template = env_component.get_template("class")
    return template.render(class_data=class_data)


def make_ex_service_content(service_name, ex_service_meta):
    template = env_component.get_template("exservicecontent")
    contents = {}
    for content in ex_service_meta:

        body = list(
            map(
                lambda x: x["name"], filter(_filter("body", "in"), content["arguments"])
            )
        )
        query = list(
            map(
                lambda x: x["name"],
                filter(_filter("query", "in"), content["arguments"]),
            )
        )
        header = list(
            map(
                lambda x: x["name"],
                filter(_filter("header", "in"), content["arguments"]),
            )
        )

        contents[content["method_name"]] = template.render(
            name=service_name,
            method=content["http_method"],
            endpoint=content["endpoint"],
            body=body,
            query=query,
            header=header,
        )
    return split_add_content_escape(contents)


def make_ex_service(name, ex_service_data, application):
    template = env_component.get_template("exservice")
    structure = []
    for ex_service, ex_service_meta in ex_service_data.items():

        ex_service = ex_service.replace("api", "service")
        ex_service_name = uppercamelcase(ex_service)

        contents = make_ex_service_content(ex_service_name, ex_service_meta)

        ex_api_json = template.render(
            name=ex_service_name,
            ex_service_meta=ex_service_meta,
            snakecase=snakecase,
            application=application,
            contents=contents,
        )
        ex_api_json = clean_json(ex_api_json)
        api_class = make_class(json.loads(ex_api_json))

        structure.append(
            {
                "type": "DATA",
                "name": f"{snakecase(ex_service_name)}.py",
                "data": black.format_str(api_class, mode=black_mode),
            }
        )

    return {"type": "PACKAGE", "name": snakecase(name), "sub": structure}


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
    return {"type": "PACKAGE", "name": "services", "sub": structure}


def make_repo_models(repo_data, application):
    sqlalchemy_template = env_component.get_template("sqlalchemymodel")

    models = [
        {"name": table, "table": snakecase(table)}
        for table in repo_data.get("x-tables", [])
    ]

    repo_model = sqlalchemy_template.render(models=models, application=application,)

    return {
        "type": "DATA",
        "name": "models.py",
        "data": black.format_str(repo_model, mode=black_mode),
    }


def make_repo(repo_data, application):
    template = env_component.get_template("repo")

    structure = []
    for repo in repo_data.keys() - ["x-tables"]:
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

    return {"type": "PACKAGE", "name": "repos", "sub": structure}


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
