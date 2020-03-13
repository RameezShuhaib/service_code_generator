from collections import defaultdict
from copy import deepcopy
from generator.utils import read_service_spec, make_file
from generator.components import make_method
from generator.generate_models import make_models
from jsonref import JsonRef


def get_endpoints(spec):
    return list(spec["paths"].keys())


def get_parameter(spec, endpoint, method="get"):
    _method = spec["paths"][endpoint][method]
    parameters = _method.get("parameters", [])

    body_param = (
        [
            _method["requestBody"]["content"]["application/json"]["schema"].get(
                "x-body-name", "body"
            )
        ]
        if bool(_method.get("requestBody"))
        else []
    )
    return [parameter["name"] for parameter in parameters] + body_param


def get_operation_for_endpoint(spec, endpoint):
    endpoints = spec["paths"][endpoint]
    return {method: endpoints[method].get("operationId") for method in endpoints.keys()}


def get_api_data(spec):
    endpoints = get_endpoints(spec)
    data = defaultdict(list)
    for endpoint in endpoints:
        operation = get_operation_for_endpoint(spec, endpoint)
        for method in operation:
            file = operation[method].split(".")[2]
            data[file].append(
                {
                    "api": operation[method].split(".")[3],
                    "parameters": get_parameter(spec, endpoint, method),
                    "http_method": method,
                }
            )
    return dict(data)


def generate_api(spec):
    resolved_spec = JsonRef.replace_refs(spec)
    api_data = get_api_data(resolved_spec)
    api_code = ""
    for api in api_data:
        for method in api_data[api]:
            _method = make_method(
                name=method["api"],
                parameters=method["parameters"],
                return_type="APIResponse",
                decorators=None,
                is_class=False,
            )
            api_code += _method
    make_file(name="api.py", directory=".", code=api_code, force_dir=False)


def generate_models(spec_file):
    models_code = make_models(spec_file)
    make_file(name="models.py", directory=".", code=models_code, force_dir=False)


def generate(spec_file):
    spec = read_service_spec(spec_file)
    generate_api(spec)
    generate_models(spec_file)
