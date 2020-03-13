from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def configure_db_with_app(app):
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
