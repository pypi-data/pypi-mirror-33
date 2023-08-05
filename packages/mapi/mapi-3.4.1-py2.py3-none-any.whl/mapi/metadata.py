# coding=utf-8

""" Metadata data classes
"""

from abc import ABCMeta
from collections import MutableMapping
from datetime import datetime as dt
from re import sub, IGNORECASE

# Compatibility for Python 2.7/3+
_AbstractClass = ABCMeta('ABC', (object,), {'__slots__': ()})

# Fields not used by mapi but seem reasonable to be set elsewhere
_EXTRA_FIELDS = {
    'extension',
    'group',
    'quality'
}


class Metadata(_AbstractClass, MutableMapping):
    """ Base Metadata class
    """

    template = ''
    fields = set()

    def __delitem__(self, key):
        raise NotImplementedError('values can be modified but keys are static')

    def __getitem__(self, key):
        # Case insensitive keys
        key = key.lower()

        # Special case for year
        if key == 'year':
            date = self._dict.__getitem__('date')
            return date[:4] if date else None
        else:
            return self._dict.__getitem__(key)

    def __init__(self, **params):
        self._dict = {k: None for k in self.fields}
        self.update(params)
        if 'template' in params:
            self.template = params['template']

    def __iter__(self):
        return {k: v for k, v in self._dict.items() if v}.__iter__()

    def __len__(self):
        return {k: v for k, v in self._dict.items() if v}.__len__()

    def __repr__(self):
        return {k: v for k, v in self._dict.items() if v}.__repr__()

    def __setitem__(self, key, value):

        # Validate key
        if key not in self.fields | _EXTRA_FIELDS:
            raise KeyError(
                "'%s' cannot be set for %s"
                % (key, self.__class__.__name__)
            )

        elif key == 'extension':
            value = value if not value or value.startswith('.') else '.' + value

        elif key == 'media' and self['media'] and self['media'] != value:
            raise ValueError('media cannot be changed')

        elif key == 'date' and value is not None:
            dt.strptime(value, '%Y-%m-%d')

        # Multi-episode hack; treat as if simply the first episode in list
        if key == 'episode' and isinstance(value, (list, tuple)):
            value = sorted(value)[0]

        # If its gotten this far, looks good
        self._dict[key] = str(value) if value else None

    def __str__(self):
        return self.format()

    def _str_replace(self, mobj):
        try:
            prefix, key, suffix = mobj.groups()
            value = self.get(key)
            assert value
            if key not in _EXTRA_FIELDS:
                value = self._str_title_case(value)
            return '%s%s%s' % (prefix, value, suffix)
        except (IndexError, KeyError, AssertionError):
            # log.warning("couldn't sub for %s" % mobj.group())
            return ''

    @staticmethod
    def _str_title_case(s):
        assert isinstance(s, str)
        lowercase_exceptions = {
            'a', 'an', 'and', 'as', 'at', 'but', 'by', 'ces', 'de', 'des',
            'du', 'for', 'from', 'in', 'la', 'le', 'nor', 'of', 'on', 'or',
            'the', 'to', 'un', 'une', 'with', 'via', 'h264', 'h265'
        }
        uppercase_exceptions = {
            'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x',
            '2d', '3d', 'au', 'aka', 'atm', 'bbc', 'bff', 'cia', 'csi', 'dc',
            'doa', 'espn', 'fbi', 'ira', 'jfk', 'la', 'lol', 'mlb', 'mlk',
            'mtv', 'nba', 'nfl', 'nhl', 'nsfw', 'nyc', 'omg', 'pga', 'rsvp',
            'tnt', 'tv', 'ufc', 'ufo', 'uk', 'usa', 'vip', 'wtf', 'wwe', 'wwi',
            'wwii', 'xxx', 'yolo'
        }
        padding_chars = '["!$\'(),-./:;<>@[]_`{} ]'
        string_lower = s.lower()
        string_length = len(s)
        s = s.title()

        # process lowercase transformations
        for exception in lowercase_exceptions:
            pos = string_lower.find(exception)
            if pos == -1: continue
            starts = pos == 0
            if starts: continue
            prev_char = string_lower[pos - 1]
            left_partitioned = prev_char in padding_chars
            word_length = len(exception)
            ends = pos + word_length == string_length
            next_char = None if ends else string_lower[pos + word_length]
            right_partitioned = ends or next_char in padding_chars
            if left_partitioned and right_partitioned:
                s = s[:pos] + exception.lower() + s[pos + word_length:]

        # process uppercase transformations
        for exception in uppercase_exceptions:
            pos = string_lower.find(exception)
            if pos == -1: continue
            starts = pos == 0
            prev_char = None if starts else string_lower[pos - 1]
            left_partitioned = starts or prev_char in padding_chars
            word_length = len(exception)
            ends = pos + word_length == string_length
            next_char = None if ends else string_lower[pos + word_length]
            right_partitioned = ends or next_char in padding_chars
            if left_partitioned and right_partitioned:
                s = s[:pos] + exception.upper() + s[pos + word_length:]
        return s

    @staticmethod
    def _str_fix_whitespace(s):
        # Concatenate dashes
        s = sub(r'-\s*-', '-', s)
        # Strip leading/ trailing dashes
        s = sub(r'-\s*$|^\s*-', '', s)
        # Concatenate whitespace
        s = sub(r'\s+', ' ', s)
        # Strip leading/ trailing whitespace
        s = s.strip()
        return s

    def format(self, template=None):
        """ Substitutes variables within template with that of fields'
        """
        s = sub(
            r'(?:<([^<]*?)\$(\w+)([^>]*?)>)',
            self._str_replace,
            template or self.template
        )
        s = self._str_fix_whitespace(s)
        return s


class MetadataTelevision(Metadata):
    """ Televesion Metadata class
    """

    template = '<$series - >< - $season><x$episode - >< - $title>'
    fields = {
        'id_imdb',
        'id_tvdb',
        'media',
        'series',
        'season',
        'episode',
        'title',
        'date',
        'synopsis',
    }

    def __init__(self, **params):
        super(MetadataTelevision, self).__init__(**params)
        self._dict['media'] = 'television'

    @staticmethod
    def _str_pad_episode(s):
        # 01x01 pattern
        s = sub(r'(?<=\s)(\d)(?=x\d)', r'0\1', s, IGNORECASE)
        s = sub(r'(?<=\dx)(\d)(?=\s|$)', r'0\1', s, IGNORECASE)
        # S01E01 pattern
        s = sub(r'([S|E])(\d)(?=\s|$|E)', r'\g<1>0\g<2>', s, IGNORECASE)
        return s

    def format(self, template=None):
        s = super(MetadataTelevision, self).format(template)
        return self._str_pad_episode(s)


class MetadataMovie(Metadata):
    """ Movie Metadata class
    """
    
    template = '<$title ><($year)>'
    fields = {
        'id_imdb',
        'id_tmdb',
        'media',
        'title',
        'date',
        'synopsis',
    }

    def __init__(self, **params):
        super(MetadataMovie, self).__init__(**params)
        self._dict['media'] = 'movie'
