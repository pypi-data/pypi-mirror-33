import json
import pathlib
import re
from abc import ABCMeta, abstractmethod

from urlymath.common.exceptions import *

PARENT = pathlib.Path(__file__).parent.parent
COUNTRIES = PARENT.joinpath('data/countries.json').as_posix()


class ELEMENTS:
    protocol = 'protocol'
    subdomain = 'subdomain'
    second_level_domain = 'sld'
    top_level_domain = 'tld'
    port = 'port'
    path = 'path'
    file = 'file'
    query = 'query'
    fragments = 'fragments'


class COMPOUNDS:
    netloc = 'netloc'
    base = 'base'
    domain = 'domain'
    full_path = 'full_path'


def parse(url: [str, 'ParsedUrl']):
    url = str(url)
    with open(COUNTRIES) as file:
        countries = json.load(file)
    cc = '|'.join(countries.keys())
    # TODO: this regex may need updating with a few extra permitted characters, upon further research...
    regex_parts = [
        # protocol
        r'^(?:(?P<protocol>[\w]+)?(?=://)(?:://))?',
        # subdomain
        r'(?:(?P<subdomain>[\w_-]+)(?=\.[\w_-]+\.[\w_-]+)(?!\.(?:ac|org|co|me|mil|gov)+\.(?:{})+)\.)?'.format(cc),
        # second and top-level domains
        r'(?:(?P<domain2>[\w_-]+)\.(?P<domain1>[\w]+(?:\.[\w]{2})?))?',
        # port
        r'(?::(?P<port>[0-9]+))?',
        # path
        r'(?:/?(?P<path>[\w/_-]+))?',
        # file
        r'(?:/(?P<file>[\w]+\.[\w]+))?',
        # query
        r'(?:(?P<query>(?:[?&][\w;,]+=[\w;,]+)*))?',
        # fragments
        r'(?:(?P<fragments>(?:[#&][\w,;]+)*))?$'
    ]

    regex = re.compile(''.join(regex_parts))
    url_parts = regex.match(url).groups(default='')
    return ParsedUrl(url_parts)


class ParsedUrl:
    def __init__(self, parts):
        self._protocol = Protocol(self, parts[0]) if parts[0] is not '' else None
        self._subdomain = SubDomain(self, parts[1]) if parts[1] is not '' else None
        self._sld = SecondLevelDomain(self, parts[2]) if parts[2] is not '' else None
        self._tld = TopLevelDomain(self, parts[3]) if parts[3] is not '' else None
        self._port = Port(self, parts[4]) if parts[4] is not '' else None
        self._path = Path(self, parts[5]) if parts[5] is not '' else None
        self._file = File(self, parts[6]) if parts[6] is not '' else None
        self._query = Query(self, parts[7]) if parts[7] is not '' else None
        self._fragments = FragmentElement(self, parts[8]) if parts[8] is not '' else None

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        self._protocol = Protocol(self, protocol)

    @property
    def subdomain(self):
        return self._subdomain

    @subdomain.setter
    def subdomain(self, subdomain):
        self._subdomain = SubDomain(self, subdomain)

    @property
    def sld(self):
        return self._sld

    @sld.setter
    def sld(self, sld):
        self._sld = SecondLevelDomain(self, sld)

    @property
    def tld(self):
        return self._tld

    @tld.setter
    def tld(self, tld):
        self._tld = TopLevelDomain(self, tld)

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        self._port = Port(self, str(port))

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = Path(self, path)

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        self._file = File(self, file)

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, query):
        self._query = Query(self, query)

    @property
    def fragments(self):
        return self._fragments

    @fragments.setter
    def fragments(self, fragments):
        self._fragments = FragmentElement(self, fragments)

    # compound elements

    @property
    def base(self):
        return self._compound(COMPOUNDS.base)

    @base.setter
    def base(self, base: str):
        self._set_compound(COMPOUNDS.base, base)

    @property
    def netloc(self):
        return self._compound(COMPOUNDS.netloc)

    @netloc.setter
    def netloc(self, netloc: str):
        self._set_compound(COMPOUNDS.netloc, netloc)

    @property
    def domain(self):
        return self._compound(COMPOUNDS.domain)

    @domain.setter
    def domain(self, domain: str):
        self._set_compound(COMPOUNDS.domain, domain)

    @property
    def full_path(self):
        return self._compound(COMPOUNDS.full_path)

    def __str__(self):
        return self.unparse()

    def __repr__(self):
        return self.unparse()

    def __iter__(self):
        return iter(self._list())

    def __next__(self):
        return self

    def __len__(self):
        return len(self.unparse())

    def __contains__(self, item):
        return item in self.unparse()

    def __add__(self, other):
        copy = parse(self)
        if isinstance(other, str):
            other = parse(other)
        if isinstance(other, UrlElement):
            other = parse(str(other))
        elif not isinstance(other, ParsedUrl):
            raise TypeError
        for element in other:
            if element is not None:
                copy.add_element(element)
        return copy

    def __sub__(self, other):
        copy = parse(self)
        if isinstance(other, str):
            other = parse(other)
        if isinstance(other, UrlElement):
            other = parse(str(other))
        if not isinstance(other, ParsedUrl):
            raise TypeError
        for element in other:
            if element is not None:
                copy.subtract_element(element)
        return copy

    def __eq__(self, other):
        return str(self) == str(other)

    def verify(self):
        if (
                (self._protocol is not None and None in [self._sld, self._tld])
                or (self._subdomain is None and None in [self._sld, self._tld])
                or (self._sld is None and None in [self._tld])
                or (self._tld is None and None in [self._sld])
        ):
            return False
        return True

    def unparse(self):
        return ''.join([item.dressed_element for item in self._list() if item is not None])

    def _list(self):
        return [
            self._protocol,
            self._subdomain,
            self._sld,
            self._tld,
            self._port,
            self._path,
            self._file,
            self._query,
            self._fragments
        ]

    def add_element(self, element):
        if isinstance(element, Protocol) and self._protocol is None:
            self._protocol = element
        elif isinstance(element, Protocol) and self._protocol is not None:
            raise UrlAdditionError
        elif isinstance(element, SubDomain) and self._subdomain is None:
            self._subdomain = element
        elif isinstance(element, SubDomain) and self._subdomain is not None:
            raise UrlAdditionError
        elif isinstance(element, SecondLevelDomain) and self._sld is None:
            self._sld = element
        elif isinstance(element, SecondLevelDomain) and self._sld is not None:
            raise UrlAdditionError
        elif isinstance(element, TopLevelDomain) and self._tld is None:
            self._tld = element
        elif isinstance(element, TopLevelDomain) and self._tld is not None:
            raise UrlAdditionError
        elif isinstance(element, Port) and self._port is None:
            self._port = element
        elif isinstance(element, Port) and self._port is not None:
            raise UrlAdditionError
        elif isinstance(element, Path) and self._path is None:
            self._path = element
        elif isinstance(element, Path) and self._path is not None:
            self._path.append(element)
        elif isinstance(element, File) and self._file is None:
            self._file = element
        elif isinstance(element, File) and self._file is not None:
            raise UrlAdditionError
        elif isinstance(element, Query) and self._query is None:
            self._query = element
        elif isinstance(element, Query) and self._query is not None:
            self._query.append(element)
        elif isinstance(element, FragmentElement) and self._fragments is None:
            self._fragments = element
        elif isinstance(element, FragmentElement) and self._fragments is not None:
            self._fragments.append(element)
        else:
            raise UrlAdditionError

    def subtract_element(self, element):
        if isinstance(element, Protocol) and self._protocol == element:
            self._protocol = None
        elif isinstance(element, Protocol) and self._protocol != element:
            raise UrlSubtractionError
        elif isinstance(element, SubDomain) and self._subdomain == element:
            self._subdomain = None
        elif isinstance(element, SubDomain) and self._subdomain != element:
            raise UrlSubtractionError
        elif isinstance(element, SecondLevelDomain) and self._sld == element:
            self._sld = None
        elif isinstance(element, SecondLevelDomain) and self._sld != element:
            raise UrlSubtractionError
        elif isinstance(element, TopLevelDomain) and self._tld == element:
            self._tld = None
        elif isinstance(element, TopLevelDomain) and self._tld != element:
            raise UrlSubtractionError
        elif isinstance(element, Port) and self._port == element:
            self._port = None
        elif isinstance(element, Port) and self._port != element:
            raise UrlSubtractionError
        elif isinstance(element, Path) and self._path == element:
            self._path.remove(element)
            if len(self._path.parsed_element) == 0:
                self._path = None
        elif isinstance(element, Path) and self._path != element:
            raise UrlSubtractionError
        elif isinstance(element, File) and self._file == element:
            self._file = None
        elif isinstance(element, File) and self._file != element:
            raise UrlSubtractionError
        elif isinstance(element, Query) and self._query == element:
            self._query.remove(element)
            if len(self._query.parsed_element) == 0:
                self._query = None
        elif isinstance(element, Query) and self._query != element:
            raise UrlSubtractionError
        elif isinstance(element, FragmentElement) and self._fragments == element:
            self._fragments.remove(element)
            if len(self._fragments.parsed_element) == 0:
                self._fragments = None
        elif isinstance(element, FragmentElement) and self._fragments != element:
            raise UrlSubtractionError
        else:
            raise UrlSubtractionError

    def remove(self, element: int):
        if element == 'protocol':
            self._protocol = None
        elif element == 'subdomain':
            self._subdomain = None
        elif element == 'sld':
            self._sld = None
        elif element == 'tld':
            self._tld = None
        elif element == 'port':
            self._port = None
        elif element == 'path':
            self._path = None
        elif element == 'file':
            self._file = None
        elif element == 'query':
            self._query = None
        elif element == 'fragments':
            self._fragments = None
        else:
            raise AttributeError

    def _compound(self, compound_element: str):
        if compound_element == 'netloc':
            netloc = [
                self._subdomain,
                self._sld,
                self._tld
            ]
            if None in netloc[1:]:
                return None
            return ''.join(item.dressed_element for item in netloc if item is not None)
        elif compound_element == 'base':
            base = [
                self._protocol,
                self._subdomain,
                self._sld,
                self._tld,
                self._port
            ]
            if None in base[2:-2] or base[0] is None:
                return None
            return ''.join(item.dressed_element for item in base if item is not None)
        elif compound_element == 'domain':
            domain = [
                self._sld,
                self._tld
            ]
            if None in domain:
                return None
            return ''.join(item.dressed_element for item in domain if item is not None)
        elif compound_element == 'full_path':
            domain = [
                self._protocol,
                self._subdomain,
                self._sld,
                self._tld,
                self._port,
                self._path,
                self._file
            ]
            if None in [domain[0], domain[2:4]]:
                return None
            return ''.join(item.dressed_element for item in domain if item is not None)

    def _set_compound(self, name, value: str):
        # netloc
        if name == 'netloc':
            dot_count = value.count('.')
            if dot_count < 1 or dot_count > 3:
                raise NonSensicalUrlStructure
            netloc = value.split('.', 2)
            if dot_count == 1:
                self._sld = SecondLevelDomain(self, netloc[0])
                self._tld = TopLevelDomain(self, netloc[1])
            if dot_count == 2:
                with open('countries.json') as file:
                    cc = json.load(file)
                    if netloc[-2] in ['ac', 'org', 'co', 'me', 'mil', 'gov'] and netloc[-1] in cc.keys():
                        self._sld = SecondLevelDomain(self, netloc[0])
                        self._tld = TopLevelDomain(self, '.'.join(netloc[1:]))
                    else:
                        self._subdomain = SubDomain(self, netloc[0])
                        self._sld = SecondLevelDomain(self, netloc[1])
                        self._tld = TopLevelDomain(self, netloc[2])
            if dot_count == 3:
                self._subdomain = SubDomain(self, netloc[0])
                self._sld = SecondLevelDomain(self, netloc[1])
                self._tld = TopLevelDomain(self, netloc[2])
        # full base
        elif name == 'base':
            protocol_sep_count = value.count('://')
            dot_count = value.count('.')
            if protocol_sep_count != 1:
                raise NonSensicalUrlStructure
            if dot_count < 1 or dot_count > 3:
                raise NonSensicalUrlStructure
            base, netloc = value.split('://')
            netloc = netloc[0].split('.', 2)
            if base[0] is not '' and base[0] is not None:
                self._protocol = Protocol(self, base[0])
            if dot_count == 1:
                self._sld = SecondLevelDomain(self, netloc[0])
                self._tld = TopLevelDomain(self, netloc[1])
            if dot_count == 2:
                with open(COUNTRIES) as file:
                    cc = json.load(file)
                    if netloc[-2] in ['ac', 'org', 'co', 'me', 'mil', 'gov'] and netloc[-1] in cc.keys():
                        self._sld = SecondLevelDomain(self, netloc[0])
                        self._tld = TopLevelDomain(self, '.'.join(netloc[1:]))
                    else:
                        self._subdomain = SubDomain(self, netloc[0])
                        self._sld = SecondLevelDomain(self, netloc[1])
                        self._tld = TopLevelDomain(self, netloc[2])
            if dot_count == 3:
                self._subdomain = SubDomain(self, netloc[0])
                self._sld = SecondLevelDomain(self, netloc[1])
                self._tld = TopLevelDomain(self, netloc[2])
        # domain
        elif name == 'domain':
            dot_count = value.count('.')
            if dot_count < 1 or dot_count > 2:
                raise NonSensicalUrlStructure
            netloc = value.split('.', 1)
            self._sld = SecondLevelDomain(self, netloc[0])
            self._tld = TopLevelDomain(self, netloc[1])


class UrlElement(metaclass=ABCMeta):
    def __init__(self, parent: ParsedUrl, element: str):
        self._parent = parent
        self._element = element
        self._parsed_element = self._parse_element(element)
        self._dressed_element = self._dress_element(element)
        self._separator = None

    @property
    def parent(self):
        return self._parent

    @property
    def element(self):
        return self._element

    @property
    def parsed_element(self):
        return self._parsed_element

    @property
    def dressed_element(self):
        return self._dressed_element

    @property
    def separator(self):
        return self._separator

    def __iter__(self):
        pass

    def __next__(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    def __repr__(self):
        return str(self._element)

    def __str__(self):
        return str(self._element)

    def __contains__(self, item):
        return item in self._parsed_element

    def __getitem__(self, item):
        return self._parsed_element[item]

    def __eq__(self, other):
        return self._element == str(other)

    @abstractmethod
    def __add__(self, other):
        pass

    @abstractmethod
    def __sub__(self, other):
        pass

    @abstractmethod
    def _parse_element(self, element):
        pass

    @abstractmethod
    def _unparse_element(self, parts):
        pass

    @abstractmethod
    def _dress_element(self, element):
        pass


class ListElement(UrlElement):
    def __init__(self, parent, element):
        super().__init__(parent, element)

    def __len__(self):
        return len(self._parsed_element)

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def append(self, part: ['ListElement', str]):
        part = self._force_str(part, UrlElement)
        parts = part.lstrip('/#').split(self._separator)
        for pt in parts:
            self._parsed_element.append(pt)
        self._element = self._unparse_element(self._parsed_element)
        self._dressed_element = self._dress_element(self._element)

    def insert(self, index: int, part: ['ListElement', str]):
        part = self._force_str(part, UrlElement)
        parts = part.lstrip('/#').split(self._separator)
        parsed_element = list(reversed(self._parsed_element))
        for pt in reversed(parts):
            parsed_element.insert(len(parsed_element) - index, pt)
        self._parsed_element = list(reversed(parsed_element))
        self._element = self._unparse_element(self._parsed_element)
        self._dressed_element = self._dress_element(self._element)

    def remove(self, part: ['ListElement', str]):
        part = self._force_str(part, UrlElement)
        part = part.lstrip('/#')
        if part not in self._element:
            raise ValueError
        parts = part.lstrip('/#').split(self._separator)
        parsed_element = list(reversed(self._parsed_element))
        for pt in parts:
            parsed_element.remove(pt)
        self._parsed_element = list(reversed(parsed_element))
        self._element = self._unparse_element(self._parsed_element)
        self._dressed_element = self._dress_element(self._element)

    def delete(self, index: int):
        del(self._parsed_element[index])
        self._element = self._unparse_element(self._parsed_element)
        self._dressed_element = self._dress_element(self._element)

    @abstractmethod
    def _parse_element(self, element):
        pass

    @abstractmethod
    def _unparse_element(self, parts):
        pass

    @abstractmethod
    def _dress_element(self, element):
        pass

    def _force_str(self, part, _type):
        if isinstance(part, _type) and type(self) != type(part):
                raise UrlAdditionError
        return str(part)


class Protocol(UrlElement):
    def __init__(self, parent: ParsedUrl, protocol: str):
        super().__init__(parent, protocol)
        self._separator = '://'

    def __len__(self):
        raise AttributeError

    def __add__(self, other):
        raise AttributeError

    def __sub__(self, other):
        raise AttributeError

    def _parse_element(self, element):
        return [element]

    def _unparse_element(self, element: str):
        return element

    def _dress_element(self, element):
        return element + '://' if element is not None else element


class SubDomain(UrlElement):
    def __init__(self, parent: ParsedUrl, subdomain: str):
        super().__init__(parent, subdomain)
        self._separator = '.'

    def __len__(self):
        raise AttributeError

    def __add__(self, other):
        raise AttributeError

    def __sub__(self, other):
        raise AttributeError

    def _parse_element(self, element):
        return [element]

    def _unparse_element(self, element: str):
        return element

    def _dress_element(self, element):
        return element + '.' if element is not None else element


class SecondLevelDomain(UrlElement):
    def __init__(self, parent: ParsedUrl, second_level_domain: str):
        super().__init__(parent, second_level_domain)
        self._separator = '.'

    def __len__(self):
        raise AttributeError

    def __add__(self, other):
        raise AttributeError

    def __sub__(self, other):
        raise AttributeError

    def _parse_element(self, element):
        return [element]

    def _unparse_element(self, element: str):
        return element

    def _dress_element(self, element):
        return element + '.' if element is not None else element


class TopLevelDomain(UrlElement):
    def __init__(self, parent: ParsedUrl, top_level_domain: str):
        super().__init__(parent, top_level_domain)

    @property
    def country(self):
        with open(COUNTRIES) as file:
            countries = json.load(file)
        parts = self.element.split('.')
        if parts[-1] in countries.keys():
            return countries[parts[-1]]
        else:
            return None

    def __len__(self):
        raise AttributeError

    def __add__(self, other):
        raise AttributeError

    def __sub__(self, other):
        raise AttributeError

    def _parse_element(self, element):
        return [element]

    def _unparse_element(self, element: str):
        return element

    def _dress_element(self, element):
        return element


class Port(UrlElement):
    def __init__(self, parent: ParsedUrl, port: str):
        super().__init__(parent, port)
        self._separator = ':'

    def __len__(self):
        raise AttributeError

    def __add__(self, other):
        raise AttributeError

    def __sub__(self, other):
        raise AttributeError

    def _parse_element(self, element):
        return [element]

    def _unparse_element(self, element: str):
        return element

    def _dress_element(self, element):
        return ':' + element if element is not None else element


class Path(ListElement):
    def __init__(self, parent: ParsedUrl, path: str):
        super().__init__(parent, path)
        self._separator = '/'

    def _parse_element(self, element):
        return [part for part in element.split('/') if part is not ''] if element is not None else element

    def _unparse_element(self, parts: list):
        return '/'.join(parts)

    def _dress_element(self, element):
        return '/' + self._element if element is not None else element


class File(UrlElement):
    def __init__(self, parent: ParsedUrl, file: str):
        super().__init__(parent, file)
        self._separator = '.'

    @property
    def filename(self):
        return self._parsed_element[0]

    @property
    def ext(self):
        return self._parsed_element[1]

    def __len__(self):
        raise AttributeError

    def __add__(self, other):
        raise AttributeError

    def __sub__(self, other):
        raise AttributeError

    def _parse_element(self, element):
        return tuple(part for part in element.split('.') if part is not '') if element is not None else element

    def _unparse_element(self, parts: list):
        return '.'.join(parts)

    def _dress_element(self, element):
        return '/' + element if element is not None else element


class Query(ListElement):
    def __init__(self, parent: ParsedUrl, query: str):
        super().__init__(parent, query)
        self._separator = '&'

    def __contains__(self, item):
        for element in self._parsed_element:
                if item in element:
                    return True

    def append(self, part: ['Query', str]):
        part = self._force_str(part, UrlElement)
        parts = part.split(self._separator)
        for pt in parts:
            if pt.count('=') != 1:
                raise NonSensicalUrlStructure
            sides = pt.lstrip('?').split('=')
            if len(sides) == 1:
                sides.append('')
            self._parsed_element.append(tuple(sides))
        self._element = self._unparse_element(self._parsed_element)
        self._dressed_element = self._dress_element(self._element)

    def insert(self, index: int, part: ['Query', str]):
        part = self._force_str(part, UrlElement)
        parts = part.lstrip('?').split(self._separator)
        parsed_element = list(reversed(self._parsed_element))
        for pt in reversed(parts):
            sides = pt.split('=')
            parsed_element.insert(len(parsed_element) - index, tuple(sides))
        self._parsed_element = list(reversed(parsed_element))
        self._element = self._unparse_element(self._parsed_element)
        self._dressed_element = self._dress_element(self._element)

    def remove(self, part: ['Query', str]):
        part = self._force_str(part, UrlElement)
        part = part.lstrip('?')
        if part not in self._element:
            raise ValueError
        parts = part.split(self._separator)
        parsed_element = list(reversed(self._parsed_element))
        for pt in parts:
            parsed_part = tuple(pt.split('='))
            parsed_element.remove(parsed_part)
        self._parsed_element = list(reversed(parsed_element))
        self._element = self._unparse_element(self._parsed_element)
        self._dressed_element = self._dress_element(self._element)

    def delete(self, index):
        del(self._parsed_element[index])
        self._element = self._unparse_element(self._parsed_element)
        self._dressed_element = self._dress_element(self._element)

    def _parse_element(self, element):
        return [tuple(sides.split('=')) for sides in element.lstrip('?').split('&')] if element is not None else element

    def _unparse_element(self, parts: list):
        return '?' + '&'.join([sides[0] + '=' + sides[1] for sides in parts])

    def _dress_element(self, element):
        return element


class FragmentElement(ListElement):
    def __init__(self, parent: ParsedUrl, fragments: str):
        super().__init__(parent, fragments)
        self._separator = '&'

    def _parse_element(self, element):
        return [part for part in element.lstrip('#').split('&') if part is not ''] if element is not None else element

    def _unparse_element(self, parts: list):
        return '#' + '&'.join(parts)

    def _dress_element(self, element):
        return element
