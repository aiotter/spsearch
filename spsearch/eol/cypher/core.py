import aiohttp
import typing
import itertools
from spsearch.classes import AttrDict
import io

endpoint = "https://eol.org/service/cypher"


class CypherExecutor:
    def __init__(self, token: typing.Union[str, typing.TextIO]):
        if isinstance(token, str):
            self.token = token
        elif isinstance(token, typing.TextIO) or isinstance(token, io.TextIOBase):
            self.token = token.read()
        else:
            raise TypeError("token has to be str or file-like.")

    async def _execute_query(self, query: str) -> dict:
        from urllib.parse import quote
        params = {"query": quote(query)}
        headers = {"Authorization": f"JWT {self.token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, headers=headers, params=params) as response:
                assert response.status == 200, f"{response.status}: {response.reason}"
                return await response.json()

    async def _paginate(self, query: str, items: int, chunk: int) -> typing.AsyncGenerator[dict, None]:
        count = 0
        while count * chunk < items:
            query += f'\nSKIP {count*chunk} LIMIT {chunk if items >= chunk else items}'
            # print(query)
            result = await self._execute_query(query)
            yield result
            count += 1

    async def execute(self, query: str, items: int = 100, chunk: int = 100) -> AttrDict:
        results = []
        async for chunk in self._paginate(query, items=items, chunk=chunk):
            results.append(chunk)

        expected_keys = ("columns", "data")
        if len(results) == 1:
            return AttrDict(results[0])
        elif all(all(k in r for r in results) for k in expected_keys):
            # ensure each result has expected_keys
            if len(set(r['columns'] for r in results)) == 1:
                # ensure each result has the same columns
                return AttrDict(**{
                    'columns': results[0]['columns'],
                    'data': list(itertools.chain.from_iterable(r['data'] for r in results))
                })
        else:
            raise UnparsableDataException(f"Data cannot be parsed.")
