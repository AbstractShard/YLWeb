from functools import wraps
import os
from flask_login import current_user, AnonymousUserMixin
from zipfile import is_zipfile
import requests
from dotenv import load_dotenv

DEFAULT_PROFILE_PATH = "static/img/profile.png"
CURRENT_PROFILE_PATH = "static/buffer/profile.png"

PROJECTS_PATH = "static/buffer/projects"

load_dotenv('.env')

HCAPTCHA_SITE_KEY = os.getenv('HCAPTCHA_SITE_KEY')
HCAPTCHA_SECRET_KEY = os.getenv('HCAPTCHA_SECRET_KEY')
RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
PROJECT_TYPES = ['Continue', 'Most-liked', 'Recent']


def verify_captcha(token, captcha_type, action=None):
    """Verify reCAPTCHA v3 or hCaptcha token and return (success, message) tuple.
    
    Args:
        token (str): The captcha token to verify
        captcha_type (str): Type of captcha ('recaptcha' or 'hcaptcha').
        action (str, optional): The action to verify for reCAPTCHA. Defaults to None.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not token:
        return False, f"{captcha_type} не пройдена."
    
    if captcha_type == 'recaptcha':
        data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': token
        }
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    elif captcha_type == 'hcaptcha':
        data = {
            'secret': HCAPTCHA_SECRET_KEY,
            'response': token
        }
        verify_url = 'https://hcaptcha.com/siteverify'
    
    try:
        result = requests.post(verify_url, data=data, timeout=5).json()
        
        if not result.get('success'):
            return False, f"{captcha_type} не прошла."
        
        if captcha_type == 'recaptcha':
            if action and result.get('action') != action:
                return False, "Неверное действие reCaptcha."
            
            if result.get('score', 0) < 0.5:
                return False, f"reCaptcha не прошла, {1 - result.get('score', 0)}% бота."
        
        return True, None
    except requests.RequestException as e:
        return False, f"Ошибка при проверке {captcha_type}: {str(e)}"


def check_buffer(func):
    @wraps(func)
    def body(*args, **kwargs):
        if not os.path.exists("static/buffer"):
            os.mkdir("static/buffer")

        if not os.path.exists(CURRENT_PROFILE_PATH):
            if not isinstance(current_user, AnonymousUserMixin):
                with open(CURRENT_PROFILE_PATH, mode="wb") as curr_img:
                    curr_img.write(current_user.img)

        if not os.path.exists("static/buffer/projects"):
            os.mkdir("static/buffer/projects")

        return func(*args, **kwargs)

    return body


def check_zip(data) -> bool:
    placeholder_path = f"{PROJECTS_PATH}/placeholder.zip"

    with open(placeholder_path, mode="wb") as my_zip:
        my_zip.write(data)

    res = is_zipfile(placeholder_path)
    os.remove(placeholder_path)

    return res


def project_to_dict(project) -> dict:
    imgs = list(map(lambda y: f"../{PROJECTS_PATH}/{project.name}/preview_imgs/{y}",
                    os.listdir(f"{PROJECTS_PATH}/{project.name}/preview_imgs")))
    if not imgs:
        imgs = ["static/img/no_project_image.jpg"]
    res = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "price": project.price,
        "created_date": project.created_date,
        "imgs": imgs
    }
    return res
