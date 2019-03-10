from typing import Mapping
from .translator import Translator

translator = Translator('./dictionary/habitats/')


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

        self.code = data['code']  # habitat code
        self.habitat = data['habitat']  # habitat
        self.suitability = data['suitability']
        self.season = data['season']
        self.majorimportance = data['majorimportance']

        # Habitat code
        # https://www.iucnredlist.org/resources/habitat-classification-scheme
        self.rank = len(self.code.split('.')) - 1

    def __str__(self):
        return f"{self.code}: {self.habitat}"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.code}: {self.habitat}>"

    def translate(self, lang: str) -> str:
        return translator.translate(lang, self.code)
