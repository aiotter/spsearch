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


class Species:
    def __init__(self, nub: int, name: str =None):
        self.nub = nub
        self.name = name

    # noinspection PyUnboundLocalVariable
    @classmethod
    async def from_name(cls, name: str) -> 'Species':
        url = (base_url / 'species').with_query(name=name)
        async for datum in _get(url):
            # nubKey が key と一致しているときは nubKey キーは存在しない
            nub = datum.get('nubKey') or datum['key']
            name = datum['canonicalName']
            return cls(nub, name)
        

    async def synonyms(self):
        url = base_url / f'species/{self.nub}/synonyms'
        results = []
        async for datum in _get(url, paging=True):
            if not results:
                results.append(datum['species'])
            results.append(datum['canonicalName'])
        return results or [self.name] if self.name else []


if __name__ == '__main__':
    from sys import argv
    import asyncio
    async def test():
        sp = await Species.from_name(argv[1])
        print(await sp.synonyms())
    asyncio.run(test())
