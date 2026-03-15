import httpx

from .config import get_settings


class APIError(Exception):
    def __init__(self, status: int, method: str, path: str, body):
        self.status = status
        self.method = method
        self.path = path
        self.body = body
        super().__init__(f"{method} {path} -> {status}: {body}")


class StalwartClient:
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
    ):
        s = get_settings()
        self._base = (base_url or s.stalwart_url).rstrip("/")
        self._token = token or s.stalwart_token
        self._http = httpx.Client(
            base_url=self._base,
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=30.0,
        )

    def _handle(self, r: httpx.Response):
        if r.status_code >= 400:
            try:
                body = r.json()
            except Exception:
                body = r.text
            raise APIError(r.status_code, r.request.method, str(r.url), body)
        if r.status_code == 204 or not r.content:
            return None
        return r.json()

    def _handle_text(self, r: httpx.Response) -> str | None:
        if r.status_code >= 400:
            try:
                body = r.json()
            except Exception:
                body = r.text
            raise APIError(r.status_code, r.request.method, str(r.url), body)
        if r.status_code == 204 or not r.content:
            return None
        return r.text

    def get(self, path: str, **kwargs):
        return self._handle(self._http.get(path, **kwargs))

    def get_text(self, path: str, **kwargs) -> str | None:
        return self._handle_text(self._http.get(path, **kwargs))

    def post(self, path: str, **kwargs):
        return self._handle(self._http.post(path, **kwargs))

    def put(self, path: str, **kwargs):
        return self._handle(self._http.put(path, **kwargs))

    def patch(self, path: str, **kwargs):
        return self._handle(self._http.patch(path, **kwargs))

    def delete(self, path: str, **kwargs):
        return self._handle(self._http.delete(path, **kwargs))
