from httpx import Response


class QAcademicoError(Exception):
    pass


class LoginError(QAcademicoError):
    pass


class ApiError(QAcademicoError):
    def __init__(self, type: str, response: Response):
        code = response.status_code
        self.message = (
            f"Falha ao obter {type}: HTTP {code} em {response.url.raw_path.decode()}"
        )
        super().__init__(self.message)

