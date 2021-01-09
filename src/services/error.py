from typing import Optional


class ApiError(Exception):
    def __init__(self, message: str, error: Optional[str], *args: object) -> None:
        super().__init__(*args)
        self.message = message
        self.error = error
