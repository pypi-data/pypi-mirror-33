# -*- coding: utf-8 -*-
import requests
import json
import bs4
import yaml
import mistune

BASE_URL = 'https://github.com/infamily/indb/tree/master/wiki'

#
# def Concept(infinity_uri):
#
#     if isinstance(infinity_uri, str):
#         _concept = json.loads(requests.get().content)
#
#     elif isinstance(infinity_uri, dict):
#         _concept = {
#             'entities': {
#                 'Q0': {
#                     'aliases':
#                        {v:[{'value':wikidata_id[v], 'language': v}]
#                         for k,v in enumerate(wikidata_id)},
#                     'claims': {}
#                 }
#             }
#         }
#         wikidata_id = 'Q0'
#
#     else:
#         return None
#
#     class Name(): pass
#
#     def _init(self, details={}, fact=False):
#         self.details = details
#         self.fact = fact
#         if self.fact:
#             self.sign = '.'
#         else:
#             self.sign = '*'
#
#         try:
#             self.alias = _alias
#         except:
#             self.alias = None
#
#         self.aliases = self.__class__.concept['entities'][wikidata_id]['aliases']
#         self.claims = self.__class__.concept['entities'][wikidata_id]['claims']
#
#     def _repr(self):
#         if self.details:
#
#     def _unicode(self):
#         return '%s%s' % (self.sign, self.alias,)
#
#     Name.__name__ = str(infinity_uri)
#     Name.__init__ = _init
#     Name.__repr__ = _repr
#     Name.__unicode__ = _unicode
#
#     return Name
#



# def DemoConcept(infinity_uri):
#
#     _languages = _concept['entities'][wikidata_id]['aliases'].keys()
#     _descriptions = _concept['entities'][wikidata_id]['descriptions']
#     _alias = get_lang(_concept['entities'][wikidata_id]['aliases'], _popular)[0]['value']
#
#
#     class Name(): pass
#
#     def _init(self, details={}, fact=False):
#         self.details = details
#
#     def _neg(self):
#         return self
#
#
#     def _set_langs(self, language_codes):
#         '''
#         INPUT
#         languages a list of language codes, in order of priority to be displayed
#         if exists
#
#         OUTPUT
#         sets the .alias, which is used in __repr__
#         '''
#         self.languages = language_codes
#         self.alias = get_lang(self.aliases, self.languages)[0]['value']
#
#
#     def _repr(self):
#         if self.details:
#
#     def _unicode(self):
#         return '%s%s' % (self.sign, self.alias,)
#
#
#     def _sub(self, other):
#         result = copy.deepcopy(self)
#
#     Name.__name__ = str(wikidata_id)
#     Name.concept = _concept
#     Name.__init__ = _init
#     Name.__unicode__ = _unicode
#     Name.__repr__ = _repr
#     Name.set_langs = _set_langs
#     Name.languages = _languages
#     Name.descriptions = _descriptions
#     Name.__doc__ =  _doc
#     Name.__neg__ = _neg
#     Name.__sub__ = _sub
#
#     return Name
#
#
#



def get_concept(path):
    '''
    Retrieves concept from a wiki page.

    :path: web url or location of file on disk

    For example:

    >>> get_concept('./wiki/percent_change.md')

    >>> get_concept('https://github.com/infamily/infinity-db/blob/master/wiki/percent_change.md#1hourly')
    '''

    page = get_source(path)

    soup = bs4.BeautifulSoup(
        mistune.markdown(page),
        'html.parser')

    target = soup.find(
        'code', {'class': 'lang-yaml'})

    concept = yaml.load(target.text)

    headers = soup.find_all('h2')

    formats = {}

    for header in headers:
        content = header.find_next_sibling()

        target = content.find(
            'code', {'class': 'lang-yaml'})

        if target:
            formats[header.text] = yaml.load(target.text)

    if concept:
        if formats:
            concept['formats'] = formats
        return concept


def get_source(path):
    if str(path).startswith('https://github.com/'):
        path = path.replace(
            'https://github.com/',
            'https://raw.githubusercontent.com/'
        ).replace('/blob/', '/')

        # GitHub has just changed:
        # X https://raw.githubusercontent.com/user/repo/wiki/title#anchor
        # O https://raw.githubusercontent.com/wiki/user/repo/title.md#1hourly
        # Is Microsoft trying to unify repos to better understand all code on GH?

        if path.startswith('https://raw.githubusercontent.com/'):
            if '/wiki/' in path:
                path = '/'.join(path.split('/wiki/'))
                path = path.replace(
                    'https://raw.githubusercontent.com/',
                    'https://raw.githubusercontent.com/wiki/'
                )
                # Affix .md
                path = path.replace('#', '.md#')


    if str(path).startswith('http'):
        page = requests.get(path).content.decode("utf-8")
    else:
        page = open(path,'r').read()

    return page
