from collections import defaultdict

from jsonref import JsonRef
from stringcase import snakecase

from generator.components import make_method, make_service, make_repo, make_api
from generator.generate_models import make_models
from generator.generate_modules import generate_modules
from generator.utils import read_service_spec, make_file, read_json


def get_parameter(spec, endpoint, method="get"):
    _method = spec["paths"][endpoint][method]
    parameters = _method.get("parameters", [])
    request_type = _method.get("x-request-body-type")
    body_param = (
        [
            {
                "name": _method["requestBody"]["content"]["application/json"][
                    "schema"
                ].get("x-body-name", "body"),
                "type": request_type,
            }
        ]
        if bool(_method.get("requestBody"))
        else []
    )
    return [{"name": parameter["name"]} for parameter in parameters] + body_param


def get_api_data(spec):

    data = defaultdict(list)

    for endpoint in spec["paths"]:
        for method in spec["paths"][endpoint]:

            api_name, method_name = spec["paths"][endpoint][method][
                "operationId"
            ].split(".")
            data[snakecase(api_name)].append(
                {
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


def generate_domain(structure, open_api, spec):

    services = make_repo(spec["x-services"], application=spec["x-Application"])
    structure["sub"].extend(services)

    models = make_models("models.py", open_api)
    structure["sub"].append(models)


def generate_store(structure, spec):

    repos = make_repo(spec["x-repos"], application=spec["x-Application"])
    structure["sub"].extend(repos)


def _make_valid(spec):
    spec["path"] = {
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
    generate_domain(structure=domain, open_api=open_api, spec=spec)

    store = next(filter(lambda x: x["name"] == "store", application["sub"]))
    generate_store(structure=store, spec=spec)

    generate_modules(data=resolved_structure, current_dir=".")
