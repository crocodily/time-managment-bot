from typing import Optional


class ApiError(Exception):
    def __init__(self, message: str, error: Optional[str], *args: object) -> None:
        super().__init__(*args)
        self.message = message
        self.error = error

    def __str__(self) -> str:
        return f'{super().__str__()} message: {self.message} error: {self.error}'
