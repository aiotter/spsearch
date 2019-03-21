import aiohttp
from typing import Sequence
from yarl import URL
from ._const import BASE_URL
from copy import deepcopy
from ..classes import AttrSeq


async def taxon_search(q: str, is_active: bool =None, taxon_id: Sequence[int] =None, parent_id: int =None,
                       rank: Sequence[int] =None, rank_level: int =None, id_above: int =None, id_below: int =None,
                       per_page: int =None, locale: str =None, preferred_place_id: int =None,
                       only_id: bool =None) -> AttrSeq:
    """Get taxa information
    https://api.inaturalist.org/v1/docs/#!/Taxa/get_taxa

    Parameters
    ----------
    q
        Name must begin with this value
    is_active
        Taxon is active
    taxon_id
        Only show taxa with this ID, or its descendants
    parent_id
        Taxon's parent must have this ID
    rank
        Taxon must have this rank
    rank_level
        Taxon must have this rank level.
        Examples: 70 (kingdom), 60 (phylum), 50 (class), 40 (order), 30 (family), 20 (genus), 10 (species), 5 (subspecies)
    id_above
        Must have an ID above this value
    id_below
        Must have an ID below this value
    per_page
        Number of results to return in a page
    locale
        Locale preference for taxon common names
    preferred_place_id
        Place preference for regional taxon common names
    only_id
        Return only the record IDs

    Returns
    -------
    List of `AttrDict`
    """

    kwargs = deepcopy(locals())
    for k in [k for k in kwargs]:
        if kwargs[k] is None:
            del kwargs[k]
        elif isinstance(kwargs[k], bool):
            kwargs[k] = str(kwargs[k]).lower()
        elif k in ['taxon_id', 'rank']:
            kwargs[k] = ','.join(str(i) for i in kwargs[k])

    url = (URL(BASE_URL) / 'taxa').with_query(**kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            assert resp.status == 200, f"{resp.status}: {resp.reason}"
            data = await resp.json()

    return AttrSeq(data['results'])


if __name__ == '__main__':
    import asyncio
    from pprint import pprint
    pprint(asyncio.run(taxon_search('Lutra lutra', is_active=True)))