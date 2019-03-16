import aiohttp
from spsearch.classes import AttrSeq
from yarl import URL
from typing import Union
from itertools import chain

base_url = URL('https://eol.org/')

async def get(url: Union[str, URL], limit: int, **kwargs):
    for k in [k for k in kwargs]:
        if kwargs[k] is None:
            del kwargs[k]
        elif not isinstance(kwargs[k], str):
            kwargs[k] = str(kwargs[k]).lower()
    url = URL(url).with_query(**kwargs)

    page = 1
    result = []
    while limit > 0:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                result.append(data['results'])
                if data['startIndex'] + data['itemsPerPage'] >= data['totalResults']:
                    return AttrSeq(chain.from_iterable(result))
                limit -= data['itemsPerPage']
                page += 1


async def search(q: str =None, limit: int =50, *, exact: bool =None, filter_by_taxon_concept_id: int =None,
                 filter_by_hierarchy_entry_id: int =None, filter_by_string: int =None, cache_ttl: int =None) -> AttrSeq:
    """Search pages.

    Parameters
    ----------
    q
        the query string
    limit
        the number of item you want to get
    exact
        will find taxon pages if the title or any synonym or common name exactly matches the search term
    filter_by_taxon_concept_id
        given an EOL page ID, search results will be limited to members of that taxonomic group
    filter_by_hierarchy_entry_id
        given a Hierarchy Entry ID, search results will be limited to members of that taxonomic group
    filter_by_string
        given a search term, an exact search will be made and that matching page will be used
        as the taxonomic group against which to filter search results
    cache_ttl
        the number of seconds you wish to have the response cached

    Returns
    -------
    list of AttrDict
        Examples:
        [{
          "id": 46559121,
          "title": "Lutra lutra",
          "link": "https://eol.org/pages/46559121",
          "content": "Lutra lutra; Lutra lutra (Linnaeus, 1758); <i>Lutra lutra</i>"
        },
        ... ]
    """
    url = base_url.with_path('/api/search/1.0.json')
    return await get(url, q=q, limit=limit, exact=exact, filter_by_taxon_concept_id=filter_by_taxon_concept_id,
                         filter_by_hierarchy_entry_id=filter_by_hierarchy_entry_id,
                         filter_by_string=filter_by_string, cache_ttl=cache_ttl)


if __name__ == '__main__':
    import asyncio
    from pprint import pprint
    pprint(asyncio.run(search('Lutra lutra', exact=True)))
