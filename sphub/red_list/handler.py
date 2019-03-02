import aiohttp
from typing import Union, Mapping, Dict, TextIO, List
from ..classes import AttrDict, AttrSeq
from .exceptions import NotFoundError
from .species import Species


base_url = 'http://apiv3.iucnredlist.org/api/v3/'


class RedListApiHandler:
    """Represent Red List API"""
    def __init__(self, token: Union[str, TextIO]):
        if isinstance(token, str):
            self.token = token
        else:
            self.token = token.read()

    async def get(self, endpoint: str, params: Mapping[str, str] = {}, base_url: str = base_url, token: bool = None,
                  **kwargs) -> Dict:
        if token is None:
            if any(s in endpoint for s in [
                '/api/v3/version',
                '/api/v3/weblink/',
                '/api/v3/website/',
                '/api/v3/taxonredirect/'
            ]):
                token = False
            else:
                token = True

        from urllib.parse import quote, urljoin
        url = urljoin(base_url, quote(endpoint))
        params = {quote(k): quote(v) for (k, v) in params.items()}
        params.update(**kwargs)
        if token:
            params.update(token=self.token)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                assert response.status == 200, f"{response.status}: {response.reason}"
                return AttrDict(await response.json())

    async def species_from_name(self, name, get_info=True) -> Species:
        """Gets species from scientific name.

        Parameters
        ----------
        name: str
            scientific name of the species.
        get_info: bool
            if True, do `get_info` at once.

        Returns
        -------
        :class:`Species`
        """
        data = await self.get(f'/api/v3/species/synonym/{name}')
        if not data['count']:
            raise NotFoundError(f'{name} not found. Is it a scientific name (Latin name)?')
        result = data['result'][0]
        species = Species(self, id=result.accepted_id, name=result.accepted_name, synonyms=data['result'])
        if get_info:
            await species.get_info()
        return species

    async def species_from_category(self, category: str) -> List[Species]:
        """Gets a list of species for the category.

        Parameters
        ----------
        category: str
            Conservation category. Must be one of the following:
            "DD", "LC", "NT", "VU", "EN", "CR", "EW", "EX", "LR/lc", "LR/nt", "LR/cd"

        Returns
        -------
        List of :class:`Species`
        """
        assert category in ("DD", "LC", "NT", "VU", "EN", "CR", "EW", "EX", "LR/lc", "LR/nt", "LR/cd")
        category = category.replace('/', '')
        data = await self.get(f'/api/v3/species/category/{category}')
        return [Species(self, sp['taxonid'], sp['scientific_name']) for sp in data['result']]

