import os
import sys
from collections import namedtuple
from json import loads

from scopus.utils import get_content, get_encoded_text

ABSTRACT_RETRIEVAL_DIR = os.path.expanduser('~/.scopus/abstract_retrieval')

if not os.path.exists(ABSTRACT_RETRIEVAL_DIR):
    os.makedirs(ABSTRACT_RETRIEVAL_DIR)


class CitationOverview(object):

    @property
    def srctype(self):
        """Return the description of a record.
        Note: This may be empty.  You probably want the abstract instead.
        """
        return self.coredata.get('srctype')

    @property
    def startingPage(self):
        """Starting page."""
        return self.coredata.get('startingPage')

    @property
    def citedby_count(self):
        """Number of articles citing the abstract."""
        return self.coredata.get('citedby-count')

    @property
    def aggregationType(self):
        """Type of source the abstract is published in."""
        return self.coredata.get('aggregationType')

    @property
    def aggregationType(self):
        """Type of source the abstract is published in."""
        return self.coredata.get('creator')

    @property
    def pageRange(self):
        """Page range."""
        return 

    @property
    def endingPage(self):
        """Ending page."""
        return self.coredata.get('endingPage')

    @property
    def eid(self):
        """The EID of the abstract (might differ from the one provided)."""
        return self.coredata.get('eid')

    @property
    def pii(self):
        """The Publication Item Identifier (PII) of the abstract."""
        return self.coredata.get('pii')
    
    @property
    def source-id(self):
        """Scopus-ID of the source the abstract is published in."""
        return self.coredata.get('source-id')

    @property
    def description(self):
        """The abstract (description) of the abstract object."""
        return self.coredata.get('description')
    
    @property
    def issueIdentifier(self):
        """Issue number for abstract."""
        return self.coredata.get('issueIdentifier')

    @property
    def issn(self):
        """ISSN of the publisher.
        Note: If E-ISSN is known to Scopus, this returns both
        ISSN and E-ISSN in random order separated by blank space.
        """
        return self.coredata.get('issn')
    
    @property
    def title(self):
        """Abstract title."""
        return self.coredata.get('title')

    @property
    def volume(self):
        """Volume for the abstract."""
        return self.coredata.get('volume')

    @property
    def url(self):
        """URL to Abstract Retrieval API view of the abstract."""
        return self.coredata.get('url')

    @property
    def identifier(self):
        """Scopus-identifier for the abstract (the right part of the EID)."""
        return self.coredata.get('identifier')

    @property
    def doi(self):
        """Document Object Identifier (DOI) of the abstract."""
        return self.coredata.get('doi')
    
    @property
    def publicationName(self):
        """Name of source the abstract is published in (e.g. the Journal)."""
        return self.coredata.get('publicationName')

    @property
    def affiliations(self):
        """A list of namedtuples storing affilation information,
        where each namedtuple corresponds to one affilation.
        The information in each namedtuple is
        (name, id, country, city).  All entries are strings.
        """
        _out = []
        _order = 'name id country city'
        _aff = namedtuple('Affiliation', _order)
        for aff in self.affs:
            _new = _aff(name=aff.get('affilname'), id=aff.get('@id'),
                        country=aff.get('affiliation-country'),
                        city=aff.get('affiliation-city'))
            _out.append(_new)
        return _out

    @property
    def language(self):
        """The language code of the abstract."""
        return self.language.get('lang')


    @property
    def authors(self):
        """A list of namedtuples storing author information,
        where each namedtuple corresponds to one author.
        The information in each namedtuple is
        (name, surname, given_name, initials, id, affiliation_ids).
        All entries are strings, exept affiliation_ids,
        which is a list of strings.
        """
        _out = []
        _order = 'name surname given_name initials id affiliation_ids'
        _auth = namedtuple('Author', _order)
        for author in self.authors:
            author = {k.split(":", 1)[-1]: v for k, v in author.items()}
            try:
                _affs = [aff.get('@id') for aff in author.get('affiliation', {})]
            except AttributeError:
                _affs = [author.get('affiliation', {}).get('@id')]
            _new = _auth(name=author.get('indexed-name'),
                         surname=author.get('surname'),
                         given_name=author.get('given-name'),
                         initials=author.get('initials'),
                         id=author.get('@auid'), affiliation_ids=_affs)
            _out.append(_new)
        return _out

    @property
    def subjectAreas(self):
        """A list of namedtuples storing subject area information,
        where each namedtuple corresponds to one subject area.
        The information in each namedtuple is
        (name, abbreviation, code).  All entries are strings.
        """
        _out = []
        _order = 'name abbreviation code'
        _area = namedtuple('SubjectArea', _order)
        for area in areas:
            _new = _area(name=area.get('$'), abbreviation=area.get('@abbrev'),
                         code=area.get('code'))
            _out.append(_new)
        return _out

    @property
    def keywords(self):
        """A list of author provided keywords."""
        return [d.get('$') for d in self.keywords]

    def __init__(self, eid, refresh=False):
        """Class to represent the results from a Scopus Abstract Retrieval.

        Parameters
        ----------
        eid : str
            The EID of the abstract.

        refresh : bool (optional, default=False)
            Whether to refresh the cached file if it exists or not.

        Notes
        -----
        The files are cached in ~/.scopus/abstract_retrieval/{eid}.
        """
        # Get file content
        qfile = os.path.join(ABSTRACT_RETRIEVAL_DIR, eid)
        url = "https://api.elsevier.com/content/abstract/eid/{}".format(eid)
        res = get_content(qfile, url=url, refresh=refresh, accept='json')
        data = loads(res.decode('utf-8'))['abstracts-retrieval-response']

        # Coredata
        self.coredata = {k.split(":", 1)[-1]: v for k, v in data['coredata'].items()}
        # Affiliations
        self.affs = data['affiliation']
        # Authors
        self.authors = data['authors']['author']
        # Language
        self.language = {k.split(":", 1)[-1]: v for k, v in data['language'].items()}
        # Keywords
        self.keywords = data['authkeywords'].get('author-keyword', [])
        # Subject areas
        self.areas = data['subject-areas'].get('subject-area', [])
        # idxterms
        self.idxterms = data['idxterms']  # not used?
        # Item
        self.items = data['item']['bibrecord']
