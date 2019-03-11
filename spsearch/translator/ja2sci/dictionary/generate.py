# noinspection PyPackageRequirements
import pandas as pd
import pickle
from pathlib import Path

here = Path(__file__).parent
dictionary = {}


# taxonomy_jp_dic
filepath = here/'raw'/'taxonomy_jp_dic.2008-03-07.txt'
df = pd.read_csv(str(filepath), sep='\t', header=None)
dictionary.update(df.iloc[:, [1, 0]].set_index(1).to_dict()[0])


# species_names.latin_vs_japanese
filepath = here/'raw'/'species_names.latin_vs_japanese.utf8.txt'
df = pd.read_csv(str(filepath), sep='\t', header=None)
dictionary.update(df.iloc[:, [1, 0]].set_index(1).to_dict()[0])


with (here / 'ja2sci.pkl').open('wb') as f:
    pickle.dump(dictionary, f)
