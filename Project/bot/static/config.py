with open("static/TOKEN", "r") as file:
    TOKEN = file.read().strip()
SELECT, CREATE, CONFIRM, EDIT,  = range(4)
BASE_URL = 'http://localhost:4000'