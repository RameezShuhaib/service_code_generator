from datamodel_code_generator import PythonVersion
from datamodel_code_generator.model.pydantic import (
    BaseModel,
    CustomRootType,
    dump_resolve_reference_action,
)

from datamodel_code_generator import snooper_to_methods
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser
from prance import BaseParser


@snooper_to_methods(max_variable_length=None)
class OpenAPIParser(JsonSchemaParser):
    def parse_raw(self) -> None:
        base_parser = BaseParser(
            spec_string=self.text, backend="openapi-spec-validator", strict=False
        )

        for obj_name, raw_obj in base_parser.specification["components"][
            "schemas"
        ].items():
            self.parse_raw_obj(obj_name, raw_obj)


def make_models(name: str, model_spec: str):

    parser = OpenAPIParser(
        BaseModel,
        CustomRootType,
        base_class="pydantic.BaseModel",
        target_python_version=PythonVersion("3.7"),
        text=model_spec,
        dump_resolve_reference_action=dump_resolve_reference_action,
    )

    return {
        "type": "DATA",
        "name": name,
        "data": parser.parse()
    }
