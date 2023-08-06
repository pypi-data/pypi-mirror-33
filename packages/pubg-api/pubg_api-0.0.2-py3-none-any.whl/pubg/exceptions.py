class PubgClientError(RuntimeError):
    pass


class TokenNotDefined(PubgClientError):
    pass


class RegionNotDefined(PubgClientError):
    pass


class Unauthorized(PubgClientError):
    pass


class NotFound(PubgClientError):
    pass


class UnsupportedMediaType(PubgClientError):
    pass


class TooManyRequests(PubgClientError):
    pass


class ApiConnectionError(PubgClientError):
    pass
