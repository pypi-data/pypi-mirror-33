"""
Parameters object sent as payload data.
"""
import json
from urllib.parse import urlencode

from .constants import (GENDER, GEOTYPE, INTERVAL, MEDIA, METRIC, ORDER,
                        PLATFORM, TONE)
from .utils.checker import (check_date, check_geocode, check_language,
                            check_list)


__all__ = (
    'InfluencerParameter',
    'SearchPublicationParameter',
    'CloudParameter',
    'PivotParameter',
    'AnalyticsParameter',
    'LocalizationParameter',
    'DistributionParameter',
    'SocialPerformanceParameter',
    'BenchmarkParameter'
)


class Parameter(dict):
    """A dict-like object used to store the payload data sent with each
    request in RadarlyApi. Each road in the API used an object (which inherits
    from this class) to build the payload data which will be sent to the API.
    When the methods of Parameter object is used to build the object, some
    checks are computed on the values in order to assert that the payload data
    are correctly made.
    """
    def __repr__(self):
        return json.dumps(self, indent=2)


class QueryMixin:
    """Mixin used to build the *query* parameter in the payload data"""
    def query(self, query):
        """A UTF-8 search query string of maximum 4K characters maximum,
        including operators. eg: “linkfluence AND radarly”. For more
        informations on how to build the query, you can check the official
        documentation.

        Args:
            query (string):
        """
        assert isinstance(query, str), 'Query shoud be a string.'
        self.update(query=query)
        return self


class PlatformMixin:
    """Mixin used to build the *platforms* parameter in the payload data.
    You can check the available options in radarly.constants module."""
    def platforms(self, *platform_list):
        """Source platforms for publications in Radarly. The available
        platforms are available in the `platforms` object in the `constants`
        module of `radarly`.

        Args:
            *platform_list (string): list of all wanted platforms"""
        PLATFORM.check(platform_list)
        self.update(platforms=list(platform_list))
        return self


class LanguageMixin:
    """Mixin used to build the *langauages* parameters in the payload data."""
    def languages(self, *language_list):
        """Restricts to the given languages, given by an ISO 639-1 code.

        Args:
            *language_list (string): list of all wanted languages
        """
        check_language(language_list)
        self.update(languages=list(language_list))
        return self


class GenderMixin:
    """Mixin used to build the *genders* parameter in the payload data"""
    def genders(self, *gender_list):
        """Restricts to the given genders.

        Args:
            *gender_list (string): list of wanted gender."""
        GENDER.check(gender_list)
        self.update(genders=list(gender_list))
        return self


class AuthorMixin:
    """Mixin used to build all the author related parameters in the payload
    data"""
    def author_birth_date(self, start=None, end=None):
        """Restrict the publications to the right interval for author's
        birthdate

        Args:
            start (datetime.datetime): Min birthdate of the author
            end (datetime.datetime): Max birthdate of the author
        """
        start = check_date(start)
        end = check_date(end)
        if start or end:
            self['birthDate'] = dict()
            if start: self['birthDate'].update(gt=start)
            if end: self['birthDate'].update(lt=end)
        return self

    def author_has_children(self, has_children):
        """Restricts to author that declare to have children.

        Args:
            has_children (boolean): whether or note the author has children
        """
        assert isinstance(has_children, bool), 'has_children must be boolean'
        self.update(hasChildren=has_children)
        return self

    def author_in_relationship(self, in_relationship):
        """Restricts to author that declare to be in a relationship

        Args:
            in_relationship (boolean): whether or not the author must be in a
                relationship"""
        assert isinstance(in_relationship, bool), 'in_relationship must be boolean'
        self.update(inRelationship=in_relationship)
        return self

    def author_verified(self, verified):
        """Restricts to author with certified accounts.

        Args:
            verified (boolean): whether or not the author has a certified
                accounts
        """
        assert isinstance(verified, bool), 'verified must be boolean'
        self.update(verified=verified)
        return self

    def author_id(self, *author):
        """Restric the set of publications to those which are created by specific
        authors.

        Args:
            author (list[Dict[str, str]]):
        """
        author_ids = [
            '(user.{platform}.id:{uid})'.format(
                platform=author_id['platform'], uid=author_id['id']
            ) for author_id in author
        ]
        author_ids = ' OR '.join(author_ids)
        query = self.get('query', '')
        self['query'] = '{} AND ({})'.format(query, author_ids) if query \
            else '({})'.format(author_ids)
        return self

class ToneMixin:
    """Mixin used to build the *tones* parameter in the payload data"""
    def tones(self, *tone_list):
        """Restricts to the given tones. All available tones are given in
        the `tones` object of the `constants` module.

        Args:
            *tone_list (string):
        """
        TONE.check(tone_list)
        self.update(tones=list(tone_list))
        return self


class MediaMixin:
    """Mixin used to build the *media* parameter in the payload data"""
    def media(self, *media_list):
        """Restricts to the given media types.

        Args:
            *media_list (string):
        """
        MEDIA.check(media_list)
        self.update(media=list(media_list))
        return self


class KeywordMixin:
    """Mixin used to build all keywords related parameter in the payload data"""
    def _builder_kw(self, name, *args):
        check_list(args, str)
        self.setdefault('keywords', {})
        self['keywords'][name] = list(args)
        return self

    def hashtags(self, *hashtags):
        """Restrics to the given hashtags.

        Args:
            *hashtags (list):
        """
        return self._builder_kw('hashtags', *hashtags)

    def mentions(self, *mentions):
        """Restrics to the given @mentions

        Args:
            *mentions (list):
        """
        return self._builder_kw('mentions', *mentions)

    def named_entities(self, *named_entities):
        """Restrics to the given named entities.

        Args:
            *named_entities (list):
        """
        return self._builder_kw('namedEntities', *named_entities)

    def keywords(self, *keywords):
        """Restrics to the given keywords (manual or trigger tags).

        Args:
            *keywords (list):
        """
        return self._builder_kw('keywords', *keywords)


class EmojiMixin:
    """Mixin used to build the *emojis* parameter in the payload data"""
    def emoji(self, charts=None, annotations=None):
        """Args:
            charts (list):
            annotations (list):
        """
        if charts or annotations:
            self['emoji'] = dict()
            if charts: self['emoji'].update(charts=charts)
            if annotations: self['emoji'].update(annotations=annotations)
        return self


class FollowerMixin:
    """Mixin used to build the *followers* parameter in the payload data"""
    def followers(self, minf=None, maxf=None):
        """Restricts to the min/max number of followers of a
        twitter/instagram/sinaweibo source."""
        if minf or maxf:
            self['followers'] = dict()
            if minf:
                assert isinstance(minf, int),  \
                    'Min values of followers must be an integer'
                self['followers'].update(gt=minf)
            if maxf:
                assert isinstance(maxf, int), \
                    'Max values of followers must be  an integer'
                self['followers'].update(lt=maxf)
        return self


class DateMixin:
    """Mixin used to build all date related parameters in the payload data"""
    def creation_date(self, created_before=None, created_after=None):
        """Restricts using indexation date"""
        created_before = check_date(created_before)
        created_after = check_date(created_after)
        if created_before or created_after:
            self['date'] = dict()
            if created_before: self['date'].update(createdBefore=created_before)
            if created_after: self['date'].update(createdAfter=created_after)
        return self

    def publication_date(self, start=None, end=None):
        """Restricts using publication date"""
        start = check_date(start)
        end = check_date(end)
        if start or end:
            if start: self.update({'from': start})
            if end: self.update(to=end)
        return self


class FlagMixin:
    """Mixin used to build the *flag* parameter in the payload data"""
    def flag(self, favorite=None, trash=None, retweet=None):
        """Enables the retrieving of favorites or non-favorites, of trashed
        publications or of retweets."""
        args = [f for f in [favorite, trash, retweet] if f]
        check_list(args, bool)
        self['flag'] = dict()
        self['flag'].update(favorite=favorite, trash=trash, rt=retweet)
        return self


class GeoMixin:
    """Mixin used to build the *geo* parameter in the payload data"""
    def geo(self, gtype, glist):
        """List of items following geo.type - fr, gb; Restricts to the
        given languages, given by an ISO 3166-1 alpha-2"""
        GEOTYPE.check(gtype)
        if gtype == GEOTYPE.COUNTRY:
            check_geocode(glist)
        self['geo'] = dict()
        self['geo']['type'] = gtype
        self['geo']['list'] = glist
        return self


class FocusMixin:
    """Mixin used to build the *focuses* parameter in the payload data"""
    def focuses(self, include=None, exclude=None):
        """List of the Radarly registred query ids you want to search into.

        Args:
            include (list): query ids to include
            exclude (list): query ids to exclude.
        """
        if include or exclude:
            self['focuses'] = []
        if include:
            check_list(include, int)
            self['focuses'].extend(
                [dict(id=query, include=True) for query in include]
            )
        if exclude:
            check_list(exclude, int)
            self['focuses'].extend(
                [dict(id=query, include=False) for query in exclude]
            )
        return self


class CorporaMixin:
    """Mixin used to build the *corpora* parameter in the payload data"""
    def corpora(self, *corpora_ids):
        """List of the Radarly registred corpora ids you want to search into"""
        check_list(corpora_ids, str)
        if corpora_ids: self.update(corpora=list(corpora_ids))
        return self


class CategoryMixin:
    """Mixin used to build the *category* parameter in the payload data"""
    def categories(self, *category_name):
        """List of the Radarly categories (listed at the end of this page)
        you want to restrict your search"""
        check_list(category_name, str)
        if category_name: self.update(categories=list(category_name))
        return self


class TagMixin:
    """Mixin used to build the *tags* parameter in the payload data"""
    def tags(self, user_tags=None, custom_fields=None):
        """List of Radarly registred influencers group tags or custom Fields
        values under format you want to restrict to."""
        self['tags'] = dict(
            customFields=custom_fields
        )
        if user_tags:
            self['tags'] = user_tags
        return self


class PaginationMixin:
    """Mixin used to build all pagination related parameters in the payload
    data"""
    def pagination(self, start=0, limit=25):
        assert isinstance(start, int), 'start index must be  an integer'
        assert isinstance(limit, int), 'limit must be  an integer'
        assert (start >= 0) and (limit > 0), 'Weird'
        self.update(start=start, limit=limit)
        return self

    def next_page(self):
        limit = self.get('limit', 25)
        start = self.get('start', -limit) + limit
        self.update(start=start, limit=limit)
        return self


class MetricsMixin:
    """Mixin used to build the *metrics* parameter in the payload data"""
    def metrics(self, *metrics_val):
        METRIC.check(metrics_val)
        self['metrics'] = list(metrics_val)
        return self


class SortMixin:
    """Mixin used to build the sort related parameter in the payload data"""
    def sort_by(self, sort_by_filter):
        assert sort_by_filter in self.AVAILABLE_SORT_BY, \
            'Unknown sortBy parameter'
        self.update(sortBy=sort_by_filter)
        return self

    def sort_order(self, sort_order_filter):
        ORDER.check(sort_order_filter.lower())
        self.update(sortOrder=sort_order_filter)
        return self


class FctxMixin:
    """Mixin used to build the *fctx* parameter in the payload data"""
    def fctx(self, *fctx_list):
        self['fctx'] = list(fctx_list)
        return self


class FieldsMixin:
    """Mixin used to build the *fields* parameter in the payload data"""
    def fields(self, *fields_list):
        self['fields'] = list(fields_list)
        return self


class TimezoneMixin:
    """Mixin used to build the *timezone* parameter in the payload data"""
    def timezone(self, time_zone):
        self['tz'] = time_zone
        return self


class IntervalMixin:
    """Mixin used to build the *interval* parameter in the payload data"""
    def interval(self, interval_value):
        INTERVAL.check(interval_value)
        self['interval'] = interval_value
        return self


class LocaleMixin:
    """Mixin used to build the *locale* parameter in the payload data"""
    def locale(self, locale_value):
        self['locale'] = locale_value
        return self


class GeoFilterMixin:
    def geofilter(self, polygon=None):
        self['geoFilter'] = dict()
        if polygon is None:
            polygon = [
                {"lon": -180, "lat": 81.01649},
                {"lon": 180, "lat": 81.01649},
                {"lon": 180, "lat": -58.94237},
                {"lon": -180, "lat": -58.94237},
                {"lon": -180, "lat": 81.01649}
            ]
        self['geoFilter']['filterPolygon'] = polygon
        return self

class StandardParameterMixin(QueryMixin,
                             PlatformMixin,
                             LanguageMixin,
                             GenderMixin,
                             AuthorMixin,
                             ToneMixin,
                             MediaMixin,
                             KeywordMixin,
                             EmojiMixin,
                             FollowerMixin,
                             FlagMixin,
                             DateMixin,
                             GeoMixin,
                             FocusMixin,
                             CorporaMixin,
                             CategoryMixin,
                             TagMixin,
                             IntervalMixin):
    """Parameter which can be  used in most of requests"""
    pass


class InfluencerParameter(Parameter,
                          StandardParameterMixin,
                          SortMixin,
                          PaginationMixin):
    """Parameter used when retrieving influencers' data"""
    AVAILABLE_SORT_BY = [
        # 'name',
        'impressions',
        'reach',
        'post'
    ]

    @classmethod
    def default(cls):
        param = cls()
        param = param.sort_by('name').sort_order('desc').pagination(0, 25)
        return param


class SearchPublicationParameter(Parameter,
                                 StandardParameterMixin,
                                 SortMixin,
                                 PaginationMixin,
                                 FctxMixin):
    """Parameters used when retrieving some publications"""
    AVAILABLE_SORT_BY = [
        'date',
        'radar.virality',
        'radar.engagement',
        'radar.reach',
        'radar.impression',
        'radar.rating',
        'random'
    ]

    @classmethod
    def default(cls):
        param = cls()
        param = param.sort_by('date').sort_order('desc').pagination(0, 25)
        return param


class CloudParameter(Parameter,
                     StandardParameterMixin,
                     MetricsMixin,
                     TimezoneMixin,
                     FieldsMixin):
    """Parameters used when retrieving cloud datas"""
    pass


class PivotParameter(Parameter,
                     StandardParameterMixin,
                     TimezoneMixin,
                     MetricsMixin,
                     FctxMixin,
                     IntervalMixin):
    """Parameters used to build pivot table"""
    def __init__(self, pivot=None, against=None):
        super().__init__()
        if pivot: self['pivot'] = pivot
        if against: self['against'] = against

    def conf(self, pivot, against):
        self['pivot'] = pivot
        self['against'] = against
        return self


class AnalyticsParameter(Parameter,
                          StandardParameterMixin,
                          FctxMixin,
                          MetricsMixin,
                          FieldsMixin):
    """Parameters used when retrieving some statistics"""
    pass


class LocalizationParameter(Parameter,
                            StandardParameterMixin,
                            LocaleMixin,
                            TimezoneMixin,
                            MetricsMixin):
    """Parameters used when retrieving a geo distribution"""
    pass


class DistributionParameter(Parameter,
                            StandardParameterMixin,
                            MetricsMixin):
    """Parameters used when retrieving a time distribution of some metrics"""
    pass


class RangeDateMixin:
    """Mixin used to build the range date parameter."""
    def date_range(self, start=None, end=None):
        start = check_date(start)
        end = check_date(end)
        if start or end:
            if start: self['from'] = start
            if end: self['to'] = end
        return self



class SocialPerformanceParameter(Parameter,
                                 RangeDateMixin,
                                 TimezoneMixin):
    """Parameters used when retrieving social performance data"""
    def platform(self, platform_value):
        right_platforms = [
            'instagram',
            'youtube',
            'twitter',
            'facebook',
            'linkedin',
            'sinaweibo'
        ]
        assert platform_value in right_platforms, \
            "The platform must be in {}".format(right_platforms)
        self['platform'] = platform_value
        return self

    def __call__(self):
        return urlencode(self)


class BenchmarkParameter(Parameter,
                         RangeDateMixin,
                         TimezoneMixin,
                         IntervalMixin):
    """Parameters used as payload when retrieving benchmark datas"""
    def entities(self, *entities_ids):
        entities_ids = [str(entities_id) for entities_id in entities_ids]
        self['entities'] = ','.join(entities_ids)
        return self


class TopicParameter(Parameter,
                     StandardParameterMixin,
                     TimezoneMixin,
                     MetricsMixin,
                     LocaleMixin):
    """Parameters used as payload when retrieving topic datas"""
    pass


class GeoParameter(Parameter,
                   StandardParameterMixin,
                   MetricsMixin,
                   FctxMixin,
                   GeoFilterMixin,
                   TimezoneMixin):
    """Parameters used as payload when retrieving geographical distribution
    datas"""
    pass


class ClusterParameter(Parameter,
                       StandardParameterMixin,
                       MetricsMixin,
                       SortMixin,
                       PaginationMixin):
    """Parameters used as payload when retrieving clusters of publications"""
    AVAILABLE_SORT_BY = [
        "volumetry",
        "radar.impression",
        "radar.reach"
    ]
