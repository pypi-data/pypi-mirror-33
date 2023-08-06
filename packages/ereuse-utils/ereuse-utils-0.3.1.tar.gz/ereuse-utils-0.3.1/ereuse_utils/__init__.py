import locale
from datetime import datetime, timedelta
from json import JSONEncoder
from uuid import UUID


class DeviceHubJSONEncoder(JSONEncoder):
    """A JSONEncoder that encodes datetimes, timedeltas, UUIDs and Enums in a compatiable way for DeviceHub's API."""

    def default(self, obj):
        if hasattr(obj, 'value'):  # an enumerated value
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj - timedelta(microseconds=obj.microseconds))
        elif isinstance(obj, UUID):
            return str(obj)
        return JSONEncoder.default(self, obj)


def ensure_utf8(app_name_to_show_on_error: str):
    """
    Python3 uses by default the system set, but it expects it to be ‘utf-8’ to work correctly. This
    can generate problems in reading and writing files and in ``.decode()`` method.
    An example how to 'fix' it:

    nano .bash_profile and add the following:
    export LC_CTYPE=en_US.UTF-8
    export LC_ALL=en_US.UTF-8
    """
    encoding = locale.getpreferredencoding()
    if encoding.lower() != 'utf-8':
        raise OSError('{} works only in UTF-8, but yours is set at {}'.format(app_name_to_show_on_error, encoding))


def now() -> datetime:
    """Returns a compatible 'now' with DeviceHub's API, this is as UTC and without microseconds."""
    return datetime.utcnow().replace(microsecond=0)
