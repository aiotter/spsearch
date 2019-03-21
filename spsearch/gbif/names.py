import aiohttp
from yarl import URL
from ..classes import AttrDict
from typing import AsyncGenerator, List

base_url = URL('http://api.gbif.org/v1/')


async def _get(url: URL, paging =False, chunk_size: int =100) -> AsyncGenerator[None, AttrDict]:
    data = {}
    offset = 0
    while not data.get('endOfRecords'):
        async with aiohttp.ClientSession() as session:
            if paging:
                url = url.with_query(offset=offset, limit=chunk_size)
            async with session.get(url) as resp:
                assert resp.status == 200, f"{resp.status}: {resp.reason}"
                data = await resp.json()

        for datum in data['results']:
            yield AttrDict(datum)
        offset += 1
        if not offset:
            break


async def get_synonyms(name) -> List[str]:
    url = (base_url / 'species').with_query(name=name)
    results = []
    async for datum in _get(url):
        nub = datum['nubKey']
        results.append(datum['canonicalName'])
        break

    # noinspection PyUnboundLocalVariable
    url = base_url / f'species/{nub}/synonyms'
    async for datum in _get(url, paging=True):
        results.append(datum['canonicalName'])
    return results


if __name__ == '__main__':
    from sys import argv
    import asyncio
    print(asyncio.run(get_synonyms(argv[1])))
