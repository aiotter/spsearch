# spsearch
Python tools to get species data from various API, including IUCN Red List and Encyclopedia of Life.


## What is spsearch?
This is a collection of CLI tools which enable you to use various API with ease.


## Why spsearch?
- **Using asyncio.**  
Unfortunately, some of the APIs are far from fastest (e.g. IUCN Red List API), so asynchronous retrieval will help you getting various info at once.


- **For easier search.**  
Some of the APIs accept the only one certain scientific name of the species to search.
For example, when you search Asian small-clawed otter with `Aonyx cinerea` via 'Individual species by name' method,
Red List API returns no result, as it is only referable in `Aonyx cinereus`.
`spsearch.RedListApiHandler.species_from_name()` both accepts `Aonyx cinerea` and `Aonyx cinereus`.


## How to use
### translator.ja2sci (translate Japanese name into scientific name)
```python
from spsearch.translator import ja2sci
print(ja2sci.convert('ユーラシアカワウソ'))  # Lutra lutra
```

### Red List API
You have to generate your own token [here](http://apiv3.iucnredlist.org/api/v3/token).
```python
from pprint import pprint
import asyncio
from spsearch.redlist import RedListApiHandler
handler = RedListApiHandler(token=YOUR_REDLIST_API_TOKEN)

async def main():
    # Get the info of Eurasian otter (Lutra lutra)
    otter = await handler.species_from_name('Lutra lutra')
    print(otter)    # [NT]Lutra lutra

    # Print some information about this species
    print(otter.category)           # NT
    print(otter.order)              # MUSTELIDAE
    print(otter.assessment_date)    # 2014-06-20

    # Get the list of the threats
    threats = await otter.get_threats()

    # Threats are returned in a container class with some convenient method
    print(threats)
        # -> CodeHierarchySeq([
        #       <Threat 1.1: Housing & urban areas>,
        #       <Threat 1.2: Commercial & industrial areas>,
        #       <Threat 1.3: Tourism & recreation areas>,
        #       <Threat 2.4: Marine & freshwater aquaculture>,
        #       <Threat 2.4.3: Scale Unknown/Unrecorded>,
        #       <Threat 4.1: Roads & railroads>,
        #       ...
        #   ])

    print(threats[2][4])
        # -> CodeHierarchySeq([
        #       <Threat 2.4: Marine & freshwater aquaculture>,
        #       <Threat 2.4.3: Scale Unknown/Unrecorded>
        #   ])

    print(threats.codes())  # [1, 2, 4, 5, 6, 7, 9]

    # Use .slice() to slice the container
    print(threats.slice(0)) # 1.1: Housing & urban areas

    # Print some data for each threats
    print(threats.code)     # 1.1
    print(threats.title)    # Housing & urban areas

    # The same methods are available for the habitats, conservation measures
    pprint(await otter.get_habitats())
    pprint(await otter.get_conservation_measures())

    # Print the list of the countries in which they live
    pprint(await otter.get_country_occurrence())

asyncio.run(main())
```

### EOL API
If you want to use the cypher API, you need a token.
Follow the guide [here](https://github.com/EOL/eol_website/blob/master/doc/api.md) to get yours.
Classical API doesn't need it.
```
Not yet prepared
```
