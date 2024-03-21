import requests

# Класс для сохранения постоянной ссылки сервера при запросах
class Session(requests.Session):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, **kwargs):
        url = self.base_url + url
        return super().request(method, url, **kwargs)