from jinja2 import Environment, FileSystemLoader

file_loader = FileSystemLoader("generator/code_templates")
env = Environment(loader=file_loader)


def initialize_app(service_name, app):
    template = env.get_template("app")

    enable_cors = app["enable_cors"] == "true"
    enable_database = app["enable_database"] == "true"
    enable_error_handler = app["enable_error_handler"] == "true"

    return template.render(
        service_name=service_name,
        enable_cors=enable_cors,
        enable_database=enable_database,
        enable_error_handler=enable_error_handler,
    )
