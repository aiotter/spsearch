from typing import Union, Mapping, List, Dict
from ..classes import AttrDict, AttrSeq
import json
from pathlib import Path
import csv

dictionary_path = './dictionary/habitats/'

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
        Habitat code.
        See details here: https://www.iucnredlist.org/resources/habitat-classification-scheme

    Returns
    -------
    str
    """
    return dictionary[lang][code]


class Habitat:
    """Represents a biome.

    Attributes
    ----------
    code : str
        Habitat code.
        See details here: https://www.iucnredlist.org/resources/habitat-classification-scheme
    habitat : str
        English description of the biome.
    suitability
    season
    majorimportance
    """
    def __init__(self, data: Mapping[str, str]):
        self._data = data

        self.code            = data['code']             # habitat code
        self.habitat         = data['habitat']          # habitat
        self.suitability     = data['suitability']
        self.season          = data['season']
        self.majorimportance = data['majorimportance']

        # Habitat code
        # https://www.iucnredlist.org/resources/habitat-classification-scheme
        self.level = len(self.code.split('.')) - 1

    def __str__(self):
        return f"{self.code}: {self.habitat}"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.code}: {self.habitat}>"

    def translate(self, lang: str) -> str:
        return translate(lang, self.code)


