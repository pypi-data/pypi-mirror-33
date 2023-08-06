import json
import json as json_lib
from urllib.parse import urlencode, urlparse, urlunparse

from flask.testing import FlaskClient
from werkzeug.wrappers import Response

JSON = 'application/json'
AUTH = 'Authorization'
BASIC = 'Basic {}'


class Client(FlaskClient):
    """
    A client for the REST servers of DeviceHub and WorkbenchServer.

    - JSON first. By default it sends and expects receiving JSON files.
    - Assert regular status responses, like 200 for GET.
    - Auto-parses a nested dictionary of URL query params to the
      URL version with nested properties to JSON.
    - Meaningful headers format: a dictionary of name-values.
    """

    def open(self, uri: str, status=200, accept=JSON, content_type=JSON,
             headers: dict = None, **kw) -> (dict or str, Response):
        """

        :param uri: The URI without basename and query.
        :param status: Assert the response for specified status. Set
        None to avoid.
        :param accept: The Accept header. If 'application/json'
        (default) then it will parse incoming JSON.
        :param headers: A dictionary of headers, where keys are header
        names and values their values.
        Ex: {'Accept', 'application/json'}.
        :param kw: Kwargs passed into parent ``open``.
        :return: A tuple with: 1. response data, as a string or JSON
        depending of Accept, and 2. the Response object.
        """
        headers = headers or {}
        headers['Accept'] = accept
        headers['Content-Type'] = content_type
        headers = [(k, v) for k, v in headers.items()]
        if 'data' in kw and content_type == JSON:
            kw['data'] = json.dumps(kw['data'])
        response = super().open(uri, headers=headers, **kw)
        if status:
            assert response.status_code == status
        data = response.get_data().decode()
        if json:
            data = json_lib.loads(data) if data else {}
        return data, response

    def get(self, uri: str, query: dict = {}, status: int = 200, accept: str = JSON,
            headers: dict = None, **kw) -> (dict or str, Response):
        """
        Performs a GET.

        See the parameters in :meth:`ereuse_utils.test.Client.open`.
        Moreover:

        :param query: A dictionary of query params. If a parameter is a
        dict or a list, it will be parsed to JSON, then all params
        are encoded with ``urlencode``
        :param kw: Kwargs passed into parent ``open``.
        """
        # Let's override query with the passed-in query param
        _, _, path, params, _, fragment = urlparse(uri)
        # Convert inner dicts and lists to json
        # We create a new dict to avoid mutating input
        q = {k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in query.items()}
        # Add everything back together
        uri = urlunparse(('', '', path, params, urlencode(q, True), fragment))
        return super().get(uri, status=status, accept=accept, headers=headers, **kw)

    def post(self, uri: str, data: str or dict, status: int = 201, content_type: str = JSON,
             accept: str = JSON, headers: dict = None, **kw):
        """
        Performs a POST.

        See the parameters in :meth:`ereuse_utils.test.Client.open`.
        """
        return super().post(uri, data=data, status=status, content_type=content_type,
                            accept=accept, headers=headers, **kw)

    def patch(self, uri: str, data: str or dict, status: int = 200, content_type: str = JSON,
              accept: str = JSON, headers: dict = None, **kw):
        """
        Performs a PATCH.

        See the parameters in :meth:`ereuse_utils.test.Client.open`.
        """
        return super().patch(uri, data=data, status=status, content_type=content_type,
                             accept=accept, headers=headers, **kw)
