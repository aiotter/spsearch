from typing import Union
from os import PathLike
from pathlib import Path
import csv


class Translator:
    """
    Parameters
    ----------
    dir_set : str or PathLike
        representative of directory which contains CSV dictionary.
    """
    def __init__(self, dir_set: Union[str, PathLike]):
        self.dictionary = {}
        if isinstance(dir_set, str):
            dir_set = Path(dir_set)
        for p in dir_set.glob('*.csv'):
            with p.open('r', encoding='utf-8') as f:
                reader = csv.reader(f)
                self.dictionary[p.stem] = {row[0]: row[1] for row in reader}

    def translate(self, lang: str, code: str) -> str:
        """Translate the code.

        Parameters
        ----------
        lang : str
            Destination language. The dictionary has to be at `dictionary_path`/`lang`.csv.
        code : str
            Code to translate.
            See details https://www.iucnredlist.org/resources/

        Returns
        -------
        str
        """
        return self.dictionary[lang][code]
