from collections import defaultdict
from typing import Dict

from jsonref import JsonRef
from stringcase import snakecase

from generator.components import make_service, make_repo, make_api
from generator.generate_models import make_models
from generator.generate_modules import generate_modules
from generator.utils import read_service_spec, read_json


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
        [{"name": "body", "type": request_type,}]
        if bool(_method.get("requestBody"))
        else []
    )
    return [
        {
            "name": parameter["name"],
            "type": map_arguments(
                parameter["schema"]["type"], parameter["schema"].get("format")
            ),
        }
        for parameter in parameters
    ] + body_param


def get_response_data(spec: Dict, endpoint: str, method: str):
    response = spec["paths"][endpoint][method]["responses"].get(200)
    if not response:
        return []
    return spec["paths"][endpoint][method]["responses"][200]["content"]["application/json"]["schema"]["oneOf"]


def get_api_data(spec):

    data = defaultdict(list)

    for endpoint in spec["paths"]:
        for method in spec["paths"][endpoint]:

            response_types = [
                response.get("x-response-type") for response in get_response_data(spec, endpoint, method)
            ]

            api_name, method_name = spec["paths"][endpoint][method][
                "operationId"
            ].split(".")
            data[snakecase(api_name)].append(
                {
                    "response_type": list(filter(lambda x: x, response_types)),
                    "method_name": method_name,
                    "arguments": get_parameter(spec, endpoint, method),
                    "http_method": method,
                }
            )
    return dict(data)


def generate_api(structure, open_api, spec):

    resolved_open_api = JsonRef.replace_refs(open_api)
    api_data = get_api_data(resolved_open_api)

    apis = make_api(spec["x-apis"], api_data, application=spec["x-Application"])
    structure["sub"].extend(apis)

    models = make_models("dtos.py", open_api)
    structure["sub"].append(models)


def generate_domain(structure, spec):

    services = make_service(spec["x-services"], application=spec["x-Application"])
    structure["sub"].extend(services)

    models = make_models("models.py", spec)
    structure["sub"].append(models)


def generate_store(structure, spec):

    repos = make_repo(spec["x-repos"], application=spec["x-Application"])
    structure["sub"].extend(repos)


def _make_valid(spec):
    spec["paths"] = {
        "/": {"get": {"responses": {200: {"description": "DummyResponse"}}}}
    }
    return spec


def generate(spec_file):
    spec = read_service_spec(spec_file)
    spec = _make_valid(spec)

    application_name = spec["x-Application"]
    open_api_file = spec["x-Spec"]

    open_api = read_service_spec(open_api_file)

    structure = read_json("generator/structure.json")
    structure["name"] = application_name
    resolved_structure = JsonRef.replace_refs(structure)

    application = next(
        filter(lambda x: x["name"] == application_name, resolved_structure["sub"])
    )
    test = next(filter(lambda x: x["name"] == "test", resolved_structure["sub"]))

    api = next(filter(lambda x: x["name"] == "api", application["sub"]))
    generate_api(structure=api, open_api=open_api, spec=spec)

    domain = next(filter(lambda x: x["name"] == "domain", application["sub"]))
    generate_domain(structure=domain, spec=spec)

    store = next(filter(lambda x: x["name"] == "store", application["sub"]))
    generate_store(structure=store, spec=spec)

    generate_modules(data=resolved_structure, current_dir=".")
