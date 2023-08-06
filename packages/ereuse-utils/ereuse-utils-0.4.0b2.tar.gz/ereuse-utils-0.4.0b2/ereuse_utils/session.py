from requests_toolbelt.sessions import BaseUrlSession


class Session(BaseUrlSession):
    """A BaseUrlSession that always raises for status."""
    def __init__(self, base_url=None):
        super().__init__(base_url)
        self.hooks['response'] = lambda r, *args, **kwargs: r.raise_for_status()
