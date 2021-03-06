from typing import TYPE_CHECKING, Union, Mapping, List, MutableSequence
from ..classes import AttrDict, AttrSeq
from .classes import CodeHierarchySeq, Synonym
from .habitats import Habitat
from .threats import Threat
from .conservation_measures import ConservationMeasure

if TYPE_CHECKING:
    from .handler import RedListApiHandler


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
                 name: str = None, synonyms: List[Synonym] = None):
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

    @property
    def authority(self):
        """
        self.authority sometimes like '(Linnaeus, 1758)' and other times like 'Bennett, 1833'
        This property wraps the attribute to return canonical form of authority without any brackets.
        """
        authority = self._data['authority']
        if authority.startswith('(') and authority.endswith(')'):
            return authority.replace('(', '').replace(')', '')
        else:
            return authority

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
        if self.got_info:
            return AttrDict(self._data)

        data = await self.handler.get(f'/api/v3/species/id/{self.id}')
        result = data['result'][0]

        self.got_info = True
        self._data = result
        self.scientific_name = result['scientific_name']

        for key in result:
            if key == 'class':
                setattr(self, key + '_', result[key])
            if key == 'authority':
                pass
            else:
                setattr(self, key, result[key])
        return AttrDict(result)

    async def get_habitats(self) -> CodeHierarchySeq:
        """Returns information about habitats of the species.

        Returns
        -------
        List of `Habitat`
        """
        data = await self.handler.get(f'/api/v3/habitats/species/id/{self.id}')
        return CodeHierarchySeq(Habitat(data=AttrDict(hab)) for hab in data['result'])

    async def get_threats(self) -> CodeHierarchySeq:
        """Returns information about threats of the species.

        Returns
        -------
        List of `Threat`
        """
        data = await self.handler.get(f'/api/v3/threats/species/id/{self.id}')
        return CodeHierarchySeq(Threat(data=AttrDict(th)) for th in data['result'])

    async def get_conservation_measures(self) -> CodeHierarchySeq:
        """Returns information about conservation measures of the species.

        Returns
        -------
        List of `ConservationMeasure`
        """
        data = await self.handler.get(f'/api/v3/measures/species/id/{self.id}')
        return CodeHierarchySeq(ConservationMeasure(data=AttrDict(con)) for con in data['result'])

    async def get_country_occurrence(self) -> MutableSequence[AttrDict]:
        """Returns list of countries in which the species exists or existed.

        Returns list of AttrDict which has following attributes:
            code:              Two-character ISO country code
            country:           Country name
            presence:          Is/was the species in this area; e.g. Extant, Possibly Extinct
            origin:            Why/how the species is in this area; e.g. Native, Introduced, Origin Uncertain
            distribution_code: Different combinations of the presence, origin and seasonality codes are
                               used to create legends for the final distribution map.
                               e.g. Native, Introduced, Present - Origin Uncertain

        Returns
        -------
        List of `AttrDict`
        """
        data = await self.handler.get(f'/api/v3/species/countries/id/{self.id}')
        return AttrSeq(data['result'])
