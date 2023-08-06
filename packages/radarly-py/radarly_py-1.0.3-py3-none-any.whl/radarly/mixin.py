"""
Mixins used by the ``radarly`` module
"""
import json
import copy
from pytz import timezone
from .api import RadarlyApi
from .utils import parse_date, to_snake_case


class AttributeMixin(dict):
    """Mixin to transform dictionary into an object where the keys of the
    dictionary are attributes of the instance"""
    def dict_to_attribute(self, data, translator=None):
        """Add all (key, value) of data in the object

        Args:
            data (dict): data to transfer to the new object
            translator (dict, optional): translator to convert some value of the dict
        Returns:
            None
        """
        translator = translator or dict()
        data = {
            to_snake_case(key): translator.get(key, lambda x: x)(data[key])
            for key in data.keys()
        }
        self.update(data)
        return None

    def __getattr__(self, key):
        translator = dict(
            created=parse_date,
            updated=parse_date,
            start=parse_date,
            date=parse_date,
            stop=parse_date,
            timezone=timezone
        )
        if key in self:
            return translator.get(key, lambda x: x)(self[key])
        log = "{} doesn't have a '{}' attribute".format(
            self.__class__.__name__,
            key
        )
        raise AttributeError(log)

    def show_source(self):
        """Display the dictionary as a normal hash table"""
        return json.loads(json.dumps(self))


class GeneratorMixin:
    """Generator which yield all items matching some payload.

    Args:
        search_param (SearchPublicationParameter):
        project_id (int):
        api (RadarlyApi):
    Yields:
        items
    """
    def __init__(self, search_param, project_id, api):
        self.api = api or RadarlyApi.get_default_api()
        self.project_id = project_id
        self.total = None
        self.search_param = copy.copy(search_param)
        self._items = None
        self.current_page = 1
        self._fetch_items()

    def __iter__(self):
        return self

    def _fetch_items(self):
        """Get next range of items"""
        raise NotImplementedError(("In order to use this mixin, you must "
                                   "implement the _fetch_items method"))

    def __next__(self):
        try:
            returned_value = next(self._items)
        except StopIteration:
            self.current_page += 1
            if self.current_page > self.total_page:
                raise StopIteration
            self._fetch_items()
            returned_value = next(self._items)
        return returned_value
