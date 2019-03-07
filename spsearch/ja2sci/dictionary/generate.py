import pandas as pd
import pickle
from pathlib import Path

here = Path(__file__).parent
df = pd.read_csv(here / 'species_names.latin_vs_japanese.utf8.txt', sep='\t', header=None)
dictionary = df.iloc[:, [1,0]].set_index(1).to_dict()[0]
with (here / 'ja2sci.pkl').open('wb') as f:
    pickle.dump(dictionary, f)
