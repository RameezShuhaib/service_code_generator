from generator.generator import generate
from generator.components import make_class
from generator.generate_modules import generate_modules
from generator.utils import read_project_structure
from jsonref import JsonRef

if __name__ == "__main__":
    # generate("spec.yaml")
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

    structure = read_project_structure("generator/structure.json")
    resolved_structure = JsonRef.replace_refs(structure)
    generate_modules(data=resolved_structure, current_dir=".")
