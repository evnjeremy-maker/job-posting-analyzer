"""User-facing failures without provider payloads or personal input."""


class InputError(Exception):
    pass


class ProviderError(Exception):
    def __init__(self, message, *, terminal=False):
        super().__init__(message)
        self.terminal = terminal


class ResponseError(Exception):
    pass


class OutputError(Exception):
    pass
