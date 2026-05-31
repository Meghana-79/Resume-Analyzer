from flask import Flask, redirect, url_for
from config import Config
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.resume import resume_bp
from utils.db import init_db


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return redirect(url_for('dashboard.dashboard'))

    @app.errorhandler(500)
    def server_error(error):
        return redirect(url_for('dashboard.dashboard'))

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)

