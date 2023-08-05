class NotImplementedWarning(Warning, NotImplementedError):
    pass

class TelegramError(Exception):
    def __init__(self, description: str, error_code: int):
        self.description = description
        self.error_code = error_code

        super().__init__(description)
