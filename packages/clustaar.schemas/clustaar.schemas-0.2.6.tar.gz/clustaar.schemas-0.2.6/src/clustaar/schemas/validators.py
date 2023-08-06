import re
from lupin.validators.match import Match


_OBJECT_ID_REGEX = re.compile(r"^[a-z0-9]{24}$", re.I)


class ObjectID(Match):
    """Validate that value conforms the mongoDB objectID format"""
    def __init__(self):
        super().__init__(_OBJECT_ID_REGEX)
