from flask import Flask, render_template
from flask_login import LoginManager
from flask_restful import Api
from dotenv import load_dotenv
import os

from db_related.data import db_session, users_resources, verify_cods_resources
from db_related.data.users import User
from blueprints.auth import auth_bp
from blueprints.projects import projects_bp
from blueprints.main import main_bp
import consts

# Load environment variables
load_dotenv('static/.env')

# Initialize Flask app
app = Flask(__name__)
api = Api(app)

# Configure app
app.config['SECRET_KEY'] = consts.APP_SECRET_KEY

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(main_bp)

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return render_template(
        "error.html",
        title="UltimateUnity",
        error="400",
        error_img="../static/img/errors/400.jpg"
    )

@app.errorhandler(401)
def unauthorized(error):
    return render_template(
        "error.html",
        title="UltimateUnity",
        error="401",
        error_img="../static/img/errors/401.jpg"
    )

@app.errorhandler(403)
def forbidden(error):
    return render_template(
        "error.html",
        title="UltimateUnity",
        error="403",
        error_img="../static/img/errors/403.jpg"
    )

@app.errorhandler(404)
def not_found(error):
    return render_template(
        "error.html",
        title="UltimateUnity",
        error="404",
        error_img="../static/img/errors/404.jpg"
    )

@login_manager.user_loader
def load_user(user_id: int) -> User:
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# API resources
api.add_resource(users_resources.UsersListResource, '/api/users')
api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')
api.add_resource(verify_cods_resources.VerifyCodeResource, '/api/verify_codes/<int:code_id>')

def main():
    db_session.global_init("db_related/db/db.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    main() 