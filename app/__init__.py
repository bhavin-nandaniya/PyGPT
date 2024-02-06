from flask import Flask


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "anysecretkey"

    # Register blueprints for different components (chat and index handlers).
    from .chat_handler import chat_handler
    from .index_handler import index_handler

    app.register_blueprint(chat_handler)
    app.register_blueprint(index_handler)

    return app
