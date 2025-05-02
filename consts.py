from functools import wraps
import os
from flask_login import current_user, AnonymousUserMixin
from db_related.data.projects import Project
from zipfile import ZipFile, is_zipfile

DEFAULT_PROFILE_PATH = "static/img/profile.png"
CURRENT_PROFILE_PATH = "static/buffer/profile.png"

PROJECTS_PATH = "static/buffer/projects"

def check_buffer(func):
    @wraps(func)
    def body(*args, **kwargs):
        # Проверка на наличие папки "buffer"
        if not os.path.exists("static/buffer"):
            os.mkdir("static/buffer")

        # Проверка на наличие файла с изображением профиля
        if not os.path.exists(CURRENT_PROFILE_PATH):
            if not isinstance(current_user, AnonymousUserMixin):
                with open(CURRENT_PROFILE_PATH, mode="wb") as curr_img:
                    curr_img.write(current_user.img)

        if not os.path.exists("static/buffer/projects"):
            os.mkdir("static/buffer/projects")

        for curr_dir, _, files in os.walk(PROJECTS_PATH):
            for filename in files:
                if not filename.endswith(".zip"):
                    os.remove(f"{curr_dir}/{filename}")

        return func(*args, **kwargs)

    return body


def check_zip(data) -> bool:
    placeholder_path = f"{PROJECTS_PATH}/placeholder.zip"

    with open(placeholder_path, mode="wb") as my_zip:
        my_zip.write(data)

    res = is_zipfile(placeholder_path)
    os.remove(placeholder_path)

    return res


def extract_project_imgs(project: Project):
    project_dir = f"{PROJECTS_PATH}/{project.id}"
    zip_dir = f"{project_dir}/project_imgs.zip"

    if not os.path.exists(project_dir):
        os.mkdir(project_dir)

    with open(zip_dir, mode="wb") as project_imgs:
        project_imgs.write(project.imgs)

    with ZipFile(zip_dir) as my_zip:
        my_zip.extractall(project_dir)

    os.remove(zip_dir)


def add_project_files(project: Project):
    with open(f"{PROJECTS_PATH}/{project.id}/project_files.zip", mode="wb") as project_files:
        project_files.write(project.files)


def project_to_dict(project: Project) -> dict:
    extract_project_imgs(project)

    res = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "price": project.price,
        "created_date": project.created_date,
        "imgs": list(map(lambda x: f"../{PROJECTS_PATH}/{project.id}/{x}", os.listdir(f"{PROJECTS_PATH}/{project.id}")))
    }
    return res