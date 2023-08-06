from pathdict.collection import StringIndexableList, PathDict


class NullableList(StringIndexableList):
    def __delitem__(self, key):
        if isinstance(key, str):
            key = int(key)
        self[key] = None


class Document(PathDict):
    """
    A PathDict subclass that automatically creates non existing keys in the
    path, and creates list elements as NullableList instances.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         create_if_not_exists=True,
                         list_class=NullableList)
