from typing import Union, Mapping, List
from ..classes import AttrDict
from .habitats import Habitat
from .threats import Threat
from .conservation_measures import ConservationMeasure


class Species:
    # noinspection PyUnresolvedReferences
    """Represents a species.
    Only id (and maybe name) parameter is available before executing `get_info`.

    Attributes
    -----------
    handler: RedListApiHandler
    got_info: bool
        done `get_info` or not.
    name: str
        A scientific name of the species.
    id: int
        Taxon id of the species in IUCN Red List.
    taxonid
    scientific_name
    kingdom
    phylum
    class_
        Replacement for class, as class is reserved for python.
    order
    family
    genus
    main_common_name
    authority
    published_year
    assessment_date
    category
    criteria
    population_trend
    marine_system
    freshwater_system
    terrestrial_system
    assessor
    reviewer
    aoo_km2
    eoo_km2
    elevation_upper
    elevation_lower
    depth_upper
    depth_lower
    errata_flag
    errata_reason
    amended_flag
    amended_reason
    """
    def __init__(self, handler: 'RedListApiHandler', id: Union[str, int],
                 name: str = None, synonyms: List[Mapping] = None):
        self._data = None
        self.category = None
        self.got_info = False
        self.handler = handler
        self.taxonid = int(id)
        self.scientific_name = name
        self.synonyms = synonyms

    @property
    def id(self):
        return self.taxonid

    @id.setter
    def id(self, v):
        self.taxonid = v

    @property
    def name(self):
        return self.scientific_name

    @name.setter
    def name(self, v):
        self.scientific_name = v

    def __str__(self):
        if self.category:
            return f"[{self.category}]{self.name}" if self.name else f"[{self.category}]NameUnknown(id={self.id})"
        else:
            return self.name if self.name else f"NameUnknown(id={self.id})"

    def __repr__(self):
        if self.category:
            return f"<{self.__class__.__name__} [{self.category}]{self.name if self.name else f'id={self.id}'}>"
        else:
            return f"<{self.__class__.__name__} {self.name if self.name else f'id={self.id}'}>"

    async def get_info(self) -> Mapping[str, str]:
        """Gets information about the species.

        Returns
        -------
        `AttrDict`
            The information you got.
        """
        data = await self.handler.get(f'/api/v3/species/id/{self.id}')
        result = data['result'][0]

        self.got_info = True
        self._data = result
        self.scientific_name = result['scientific_name']

        for key in result:
            if key == 'class':
                setattr(self, key + '_', result[key])
            else:
                setattr(self, key, result[key])
        return AttrDict(result)

    async def get_habitats(self) -> List[Habitat]:
        """Returns information about habitats of the species.

        Returns
        -------
        List of `Habitat`
        """
        data = await self.handler.get(f'/api/v3/habitats/species/id/{self.id}')
        return [Habitat(AttrDict(hab)) for hab in data['result']]

    async def get_threats(self) -> List[Threat]:
        """Returns information about threats of the species.

        Returns
        -------
        List of `Threat`
        """
        data = await self.handler.get(f'/api/v3/threats/species/id/{self.id}')
        return [Threat(AttrDict(th)) for th in data['result']]

    async def get_conservation_measures(self) -> List[ConservationMeasure]:
        """Returns information about conservation measures of the species.

        Returns
        -------
        List of `ConservationMeasure`
        """
        data = await self.handler.get(f'/api/v3/measures/species/id/{self.id}')
        return [ConservationMeasure(AttrDict(con)) for con in data['result']]
