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

    async def species_from_id_ensured(self, id, get_info=False) -> Species:
        """Gets species from IUCN taxon ID.
        Detect the new ID if it has been changed from the given ID.

        Note: Slow but certain way of getting species.
        Retrieves all redirect until it reaches the final destination url.

        Parameters
        ----------
        id: str or int
            Taxon ID of the species. Old one is accepted.
        get_info: bool, default False
            If True, do `get_info` at once.
            Note that the default is False, as `species_from_id` is mainly used when you need `Species` as fast as you can.

        Returns
        -------
        :class:`Species`
        """
        async with aiohttp.ClientSession() as session:
            async with session.head(f'http://apiv3.iucnredlist.org/api/v3/taxonredirect/{id}',
                                    allow_redirects=True) as resp:
                url = resp.url
                assert url.host == 'www.iucnredlist.org', f'Species for id {id} not found.'
        current_id = int(url.path.split('/')[-1])
        species = Species(self, current_id)
        if get_info:
            await species.get_info()
        return species

    async def species_from_id(self, id, get_info=False) -> Species:
        """Gets species from IUCN taxon ID.
        Detect the new ID if it has been changed from the given ID.

        Note: Approx. 3x faster than `species_from_id_ensured` but unreliable.
        Only retrieves the first redirect, so there is a chance of not reaching the final destination url.

        Parameters
        ----------
        id: str or int
            Taxon ID of the species. Old one is accepted.
        get_info: bool, default False
            If True, do `get_info` at once.
            Note that the default is False, as `species_from_id` is mainly used when you need `Species` as fast as you can.

        Returns
        -------
        :class:`Species`
        """
        async with aiohttp.ClientSession() as session:
            async with session.head(f'http://apiv3.iucnredlist.org/api/v3/taxonredirect/{id}',
                                    allow_redirects=False) as resp:
                assert int(resp.status/100) == 3, f'Species for id {id} not found.'
                url = resp.headers['Location']
        current_id = int(url.split('/')[-1])
        species = Species(self, current_id)
        if get_info:
            await species.get_info()
        return species

    async def species_from_synonym(self, name, get_info=True) -> Species:
        """Gets species from scientific name and synonym.

        Parameters
        ----------
        name: str
            scientific name of the species.
        get_info: bool, default True
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

    async def species_from_name(self, name) -> Species:
        """Gets species from canonical scientific name accepted in IUCN Red List.
        This method uses the same API endpoint as Species.get_info(),
        so all the information is already given.
        No need to run Species.get_info() after this method.

        Parameters
        ----------
        name: str
            canonical scientific name of the species.

        Returns
        -------
        :class:`Species`
        """
        data = await self.get(f'/api/v3/species/{name}')
        if 'result' not in data or not data['result']:
            raise NotFoundError(f'{name} not found. Is it a scientific name (Latin name)?')
        result = data['result'][0]
        species = Species(self, id=result.taxonid, name=result.scientific_name)

        species.got_info = True
        species._data = result
        for key in result:
            if key == 'class':
                setattr(species, key + '_', result[key])
            else:
                setattr(species, key, result[key])
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

    async def species_from_country(self, country: str) -> List[Species]:
        """Gets a list of species in the country.

        Parameters
        ----------
        country: str
            2-character ISO code of the country.
            If it is not a ISO code, it will be converted to the code via `pycountry`.

        Returns
        -------
        List of :class:`Species`
        """
        if len(country) != 2:
            import pycountry
            country = pycountry.countries.lookup(country).alpha_2
        data = await self.get(f'/api/v3/country/getspecies/{country}')
        return [Species(self, sp['taxonid'], sp['scientific_name']) for sp in data['result']]

