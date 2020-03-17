from collections import defaultdict
from typing import Dict

from jsonref import JsonRef
from stringcase import snakecase

from generator.components import (
    make_service,
    make_repo,
    make_api,
    make_ex_service,
    make_repo_models,
)
from generator.test_components import make_test_service
from generator.generate_models import make_models
from generator.generate_modules import generate_modules
from generator.utils import read_spec, read_json


OPEN_API_PRIMITIVES_MAPPING = {
    "number": "float",
    "integer": "int",
    "string": "str",
    "boolean": "bool",
    "array": "List",
}


def map_arguments(type, format):

    if format == "uuid":
        return "UUID"
    elif format == "date":
        return "date"
    elif format == "date-time":
        return "datetime"

    return OPEN_API_PRIMITIVES_MAPPING[type]


def backup_ref(spec: Dict):
    if isinstance(spec, list):
        return [backup_ref(s) for s in spec]
    if isinstance(spec, dict):
        spec_cpy = {}
        for s in spec:
            if s == "$ref":
                spec_cpy["x-ref"] = spec[s].split("/")[-1]
            spec_cpy[s] = spec[s]
        return {s: backup_ref(spec_cpy[s]) for s in spec_cpy}
    return spec


def get_parameter(spec, endpoint, method="get"):
    _method = spec["paths"][endpoint][method]
    parameters = _method.get("parameters", [])
    request_type = _method.get("x-request-body-type")
    body_param = (
        [{"name": "body", "type": request_type, "in": "body"}]
        if bool(_method.get("requestBody"))
        else []
    )
    return [
        {
            "name": parameter["name"],
            "type": map_arguments(
                parameter["schema"]["type"], parameter["schema"].get("format")
            ),
            "in": parameter["in"],
        }
        for parameter in parameters
    ] + body_param


def get_response_data(spec: Dict, endpoint: str, method: str):
    response = spec["paths"][endpoint][method]["responses"].get(200)
    if not response:
        return []
    return spec["paths"][endpoint][method]["responses"][200]["content"][
        "application/json"
    ]["schema"]["oneOf"]


def get_open_api_data(open_api):

    data = defaultdict(list)

    for endpoint in open_api["paths"]:
        for method in open_api["paths"][endpoint]:

            response_types = [
                response.get("x-response-type")
                for response in get_response_data(open_api, endpoint, method)
            ]

            api_name, method_name = open_api["paths"][endpoint][method][
                "operationId"
            ].split(".")
            data[snakecase(api_name)].append(
                {
                    "endpoint": endpoint,
                    "response_type": list(filter(lambda x: x, response_types)),
                    "method_name": method_name,
                    "arguments": get_parameter(open_api, endpoint, method),
                    "http_method": method,
                }
            )
    return dict(data)


def generate_ex_service(spec):

    structure = []
    for ex_service, ex_service_data in spec["x-ex-services"].items():
        ex_service_open_api = read_spec(ex_service_data["spec"])
        resolved_ex_service_open_api = JsonRef.replace_refs(ex_service_open_api)
        open_api_data = get_open_api_data(resolved_ex_service_open_api)
        ex_service_models = make_models("models.py", ex_service_open_api)
        ex_service_structure = make_ex_service(
            name=ex_service,
            ex_service_data=open_api_data,
            application=spec["x-Application"],
        )
        ex_service_structure["sub"].append(ex_service_models)

        structure.append(ex_service_structure)
    return {"type": "PACKAGE", "name": "ex_service", "sub": structure}


def generate_api(structure, test_structure, open_api, spec):

    resolved_open_api = JsonRef.replace_refs(open_api)
    api_data = get_open_api_data(resolved_open_api)

    apis = make_api(spec["x-apis"], api_data, application=spec["x-Application"])
    structure["sub"].extend(apis)

    models = make_models("models.py", open_api)
    structure["sub"].append(models)


def generate_domain(structure, test_structure, spec):

    # Generate service
    services = make_service(spec["x-services"], application=spec["x-Application"])
    structure["sub"].append(services)

    services_test = make_test_service(spec, application=spec["x-Application"])
    test_structure["sub"].append(
        {"type": "PACKAGE", "name": "domain", "sub": [services_test]}
    )

    # Generate ex-services
    ex_service_structure = generate_ex_service(spec)
    structure["sub"].append(ex_service_structure)

    # Generate domain models
    models = make_models("models.py", spec)
    structure["sub"].append(models)


def generate_store(structure, test_structure, spec):

    repos = make_repo(spec["x-repos"], application=spec["x-Application"])
    structure["sub"].append(repos)

    repo_model = make_repo_models(spec["x-repos"], application=spec["x-Application"])
    structure["sub"].append(repo_model)


def _make_valid(spec):
    spec["paths"] = {
        "/": {"get": {"responses": {200: {"description": "DummyResponse"}}}}
    }
    return spec


def generate(spec_file):
    spec = read_spec(spec_file)
    spec = _make_valid(spec)

    application_name = spec["x-Application"]
    open_api_file = spec["x-Spec"]

    open_api = read_spec(open_api_file)

    structure = read_json("generator/structure.json")
    structure["name"] = application_name
    resolved_structure = JsonRef.replace_refs(structure)

    application = next(
        filter(lambda x: x["name"] == application_name, resolved_structure["sub"])
    )
    test = next(filter(lambda x: x["name"] == "test", resolved_structure["sub"]))

    api = next(filter(lambda x: x["name"] == "api", application["sub"]))
    generate_api(structure=api, test_structure=test, open_api=open_api, spec=spec)

    domain = next(filter(lambda x: x["name"] == "domain", application["sub"]))
    generate_domain(structure=domain, test_structure=test, spec=spec)

    store = next(filter(lambda x: x["name"] == "store", application["sub"]))
    generate_store(structure=store, test_structure=test, spec=spec)

    generate_modules(data=resolved_structure, current_dir=".")
