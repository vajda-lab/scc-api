from requests.auth import AuthBase



class TokenAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, request):
        request.headers["Authorization"] = f"Token {self.token}"
        return request
