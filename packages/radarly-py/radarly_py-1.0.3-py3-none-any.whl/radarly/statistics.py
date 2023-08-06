"""
Time distribution of some metrics
"""

from .api import RadarlyApi
from .constants import STAT_FIELD


class Statistics(dict):
    """Dict-like object. Each key gives access to a specific kind of stats.
    This object can be explored with ``pandas``.

    >>> import pandas as pd
    >>> stats
    Statistics(fields=['occupations', 'languages', ..., 'logos', 'genders'])
    >>> languages = pd.DataFrame(stats['languages'])
    >>> languages.head()
                    af   ar  ar-bz  bg  bn  ca  cs   da  de  dv  ...     th  \\
    doc 2018-01-01 NaN   79    1.0   9 NaN  11   6  NaN  22 NaN  ...    214
        2018-01-02 NaN  199    NaN  30 NaN   6   6  7.0  27 NaN  ...    275
        2018-01-03 NaN  132    1.0  13 NaN   4   3  1.0  40 NaN  ...    207
        2018-01-04 NaN  109    NaN  10 NaN   5   3  7.0  43 NaN  ...    212
        2018-01-05 NaN   83    NaN  13 NaN   9   6  8.0  36 NaN  ...    206
    ...
    """
    path_url = '/projects/{project_id}/insights.json'
    path_occupation_url = '/projects/{project_id}/insights/occupation.json'

    def __init__(self, data, focuses=None):
        super().__init__()
        if focuses is None: focuses = lambda x: x
        translator = dict(
            focuses=focuses
        )
        self.setdefault('total', {'total': {}})
        self.setdefault('counts', {})
        for dot in data['dots']:
            dot_date = dot['date']

            self['total']['total'][dot_date] = dot['total']
            for major in dot['counts'].keys():
                self['counts'].setdefault(major, {})
                self['counts'][major][dot_date] = dot['counts'][major]
            _ = [self.setdefault(key, {}) for key in dot['stats'].keys()]

            for major in dot['stats'].keys():
                temp = {
                    translator.get(major, lambda x: x)(item['term']): {
                        (metric, dot_date):
                            item['counts'][metric]
                        for metric in item['counts']
                    } for item in dot['stats'][major]
                }
                for tone_field in temp:
                    self[major].setdefault(tone_field, {})
                    self[major][tone_field].update(temp[tone_field])

    def __repr__(self):
        return 'Statistics(fields={})'.format(list(self.keys()))

    @classmethod
    def fetch(cls, project_id, search_parameter,
              focuses=None, api=None):
        """Retrieve some insights from the API.

        Args:
            project_id (int):
            search_parameter (StatisticsParameter):
            focuses (dict): used to translate headers if 'focuses' was asked
            api (RadarlyApi, optional):
        Returns:
            Statistics
        """
        api = api or RadarlyApi.get_default_api()
        url = cls.path_url.format(project_id=project_id)

        is_occupation_asked = STAT_FIELD.OCCUPATIONS in search_parameter.get(
            'fields', []
        )
        if is_occupation_asked:
            search_parameter['fields'].remove(STAT_FIELD.OCCUPATIONS)
        data = api.post(url, data=search_parameter)

        if is_occupation_asked:
            _ = search_parameter.pop('fields')
            url = cls.path_occupation_url.format(project_id=project_id)
            occupations_data = api.post(url, data=search_parameter)
            data['dots'] += occupations_data['dots']

        return cls(data, focuses)
