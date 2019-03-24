from typing import Mapping
from .translator import Translator
from pathlib import Path

translator = Translator(Path(__file__).parent/'dictionary/habitats/')


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

    def __init__(self, code: str =None, habitat: str =None,  data: Mapping[str, str] =None):
        self._data = data

        self.code = code or data and data['code']  # habitat code
        self.habitat = habitat or data and data['habitat']  # habitat
        self.suitability = data and data['suitability']
        self.season = data and data['season']
        self.majorimportance = data and data['majorimportance']

        # Habitat code
        # https://www.iucnredlist.org/resources/habitat-classification-scheme
        self.rank = len(self.code.split('.')) - 1

    def __str__(self):
        return f"{self.code}: {self.habitat}"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.code}: {self.habitat}>"

    def translate(self, lang: str) -> str:
        return translator.translate(lang, self.code)
