from typing import Mapping
from .translator import Translator
from pathlib import Path

translator = Translator(Path(__file__).parent/'dictionary/threats/')


class Threat:
    """Represents a threat.

    Attributes
    ----------
    code : str
        Threat code.
        See details here: https://www.iucnredlist.org/resources/threat-classification-scheme
    title : str
        English description of the threat.
    threat : str
        alias for title
    timing
    scope
    severity
    score
    invasive
    """

    def __init__(self, code: str =None, title: str =None, data: Mapping[str, str] =None):
        self._data = data

        self.code = code or data and data['code']  # threat code
        self.title = title or data and data['title']  # threat type
        self.threat = self.title  # alias for title
        self.timing = data and data['timing']
        self.scope = data and data['scope']
        self.severity = data and data['severity']
        self.score = data and data['score']
        self.invasive = data and data['invasive']

        # Threat code
        # https://www.iucnredlist.org/resources/threat-classification-scheme
        self.rank = len(self.code.split('.')) - 1

    def __str__(self):
        return f"{self.code}: {self.title}"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.code}: {self.title}>"

    def translate(self, lang: str) -> str:
        return translator.translate(lang, self.code)
