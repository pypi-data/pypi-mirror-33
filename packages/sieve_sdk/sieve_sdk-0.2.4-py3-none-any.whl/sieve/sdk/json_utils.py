import json
import datetime
from decimal import Decimal
from functools import partial

from sieve.sdk import config
from pathdict.collection import StringIndexableList, PathDict


def default_handler(value):
    if isinstance(value, datetime.datetime):
        return value.strftime(config.DATETIME_FORMAT)
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, PathDict):
        return dict(value)
    elif isinstance(value, StringIndexableList):
        return list(value)
    raise TypeError("Unexpected type")


dumps = partial(json.dumps, default=default_handler)
