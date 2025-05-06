from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from db_related.data import db_session
from db_related.data.users import User
from consts import check_buffer

# Initialize blueprint
main_bp = Blueprint('main', __name__)

# Routes
@main_bp.route("/")
@check_buffer
def index():
    return render_template("index.html", title="Главная")

@main_bp.route("/about")
@check_buffer
def about():
    return render_template("about.html", title="О нас")

@main_bp.route("/contact")
@check_buffer
def contact():
    return render_template("contact.html", title="Контакты")

@main_bp.route("/search")
@check_buffer
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template("search.html", title="Поиск", results=[])
    
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.name.ilike(f'%{query}%')).all()
    
    return render_template("search.html", title="Поиск", results=users)

@main_bp.route("/api/user/<int:user_id>")
@login_required
@check_buffer
def get_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_date": user.created_date.isoformat()
    }) 