from flask import redirect, url_for, render_template, Response

from config import Config
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.landing import landing_bp
from routes.resume import resume_bp
from utils.db import init_db



def create_app():
    from flask import Flask

    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config.from_object(Config)

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        # Avoid redirecting to /dashboard; it can mask the real 404/loop issues.
        return render_template('landing.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        # Avoid redirecting to /dashboard; it can mask the real 500 and create loops.
        return (
            render_template('landing.html'),
            500,
        )





    return app



app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

