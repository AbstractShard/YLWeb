# Testing projects apis

from requests import post

with open("403.zip", "rb") as files_f, open("403.zip", "rb") as imgs_f:
    files = {
        'files': files_f,
        'imgs': imgs_f
    }
    data = {
        'name': 'Test Project',
        'description': 'Test Description',
        'price': 100,
        'created_by_user_id': 1
    }
    response = post('http://localhost:5000/api/projects', data=data, files=files)
    print(response.json())