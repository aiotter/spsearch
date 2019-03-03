from typing import Mapping
from pathlib import Path
import csv

dictionary_path = './dictionary/threats/'

dictionary = {}
for p in Path(dictionary_path).glob('*.csv'):
    with p.open('r', encoding='utf-8') as f:
        reader = csv.reader(f)
        dictionary[p.stem] = {row[0]: row[1] for row in reader}


def translate(lang: str, code: str) -> str:
    """Translate the code.

    Parameters
    ----------
    lang : str
        Destination language. The dictionary has to be at `dictionary_path`/`lang`.csv.
    code : str
        Threat code.
        See details https://www.iucnredlist.org/resources/threat-classification-scheme

    Returns
    -------
    str
    """
    return dictionary[lang][code]


class Threat:
    """Represents a threat.

    Attributes
    ----------
    code : str
        Threat code.
        See details here: https://www.iucnredlist.org/resources/threat-classification-scheme
    title : str
        English description of the threat.

    """

    def __init__(self, data: Mapping[str, str]):
        self._data = data

        self.code = data['code']  # threat code
        self.title = data['title']  # threat type
        self.threat = self.title  # alias for title
        self.timing = data['timing']
        self.scope = data['scope']
        self.severity = data['severity']
        self.score = data['score']
        self.invasive = data['invasive']

        # Habitat code
        # https://www.iucnredlist.org/resources/habitat-classification-scheme
        self.level = len(self.code.split('.')) - 1

    def __str__(self):
        return f"{self.code}: {self.title}"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.code}: {self.title}>"

    def translate(self, lang: str) -> str:
        return translate(lang, self.code)
