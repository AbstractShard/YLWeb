from functools import wraps
import os

from flask_login import current_user

DEFAULT_PROFILE_PATH = "static/img/profile.png"
CURRENT_PROFILE_PATH = "static/buffer/profile.png"


def check_buffer(func):
    @wraps(func)
    def body(*args, **kwargs):
        # Проверка на наличие файла с изображением профиля
        if not os.path.exists(CURRENT_PROFILE_PATH):
            with open(CURRENT_PROFILE_PATH, mode="wb") as curr_img:
                curr_img.write(current_user.img)

        return func(*args, **kwargs)

    return body