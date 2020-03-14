from generator.generator import (
    generate,
    # generate_models,
    # generate_services,
    # generate_repo,
    generate_api,
)
from generator.components import make_class
from generator.generate_modules import generate_modules
from generator.utils import read_json
from jsonref import JsonRef


if __name__ == "__main__":
    # generate("spec.yaml")
    # generate_models("service_spec.yaml")
    generate("service_spec.yaml")
    # generate_api("service_spec.yaml", "service.yaml")
    # data = {
    #     "type": "class",
    #     "name": "ServiceA",
    #     "inherits": "serviceB",
    #     "decorators": [
    #         "@singleton",
    #     ],
    #     "constructor": {
    #         "decorators": [
    #             "@inject"
    #         ],
    #         "arguments": [
    #             {
    #                 "name": "arg1",
    #                 "type": "int",
    #                 "value": 2
    #             }
    #         ],
    #         "contents": [
    #             "a=10",
    #             "b=20"
    #         ]
    #     },
    #     "attributes": [
    #         {
    #           "name": "attrib_1",
    #           "type": "int",
    #           "value": 2
    #         },
    #         {
    #             "name": "attrib_2",
    #             "type": "str",
    #         },
    #         {
    #             "name": "attrib_3",
    #             "value": "True"
    #         }
    #     ],
    #     "methods": [
    #         {
    #             "name": "function_abc",
    #             "decorators": [
    #                 "@inject",
    #             ],
    #             "arguments": [
    #                 {
    #                     "name": "arg1",
    #                     "type": "",
    #                     "value": 2
    #                 }
    #             ],
    #             "return_type": None,
    #             "contents": [
    #                 "a=10",
    #                 "b=3"
    #             ]
    #         },
    #         {
    #             "name": "function_abc",
    #             "arguments": [
    #                 {
    #                     "name": "arg1",
    #                     "type": "",
    #                     "value": 2
    #                 },
    #                 {
    #                     "name": "attrib_2",
    #                     "type": "str",
    #                 },
    #                 {
    #                     "name": "attrib_3",
    #                     "value": "True"
    #                 },
    #             ],
    #             "return_type": "bool",
    #             "contents": [
    #                 "a=10",
    #                 "b=3"
    #             ]
    #         }
    #     ],
    # }
    # print(make_class(data))
    # generate_services("service_spec.yaml")
