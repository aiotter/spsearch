import aiohttp
from spsearch.classes import AttrSeq, AttrDict
from yarl import URL
from typing import Union, List
from itertools import chain
from copy import deepcopy

base_url = URL('https://eol.org/')


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
    kwargs = deepcopy(locals())
    url = URL(base_url.with_path('/api/search/1.0.json'))

    for k in [k for k in kwargs]:
        if kwargs[k] is None or k == 'limit':
            del kwargs[k]
        elif not isinstance(kwargs[k], str):
            kwargs[k] = str(kwargs[k]).lower()
    url = url.with_query(**kwargs)

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


async def pages(id: Union[str, int], *, batch: bool =False,
                images_per_page: int =None, images_page: int =1,
                videos_per_page: int = None, videos_page: int =1,
                sounds_per_page: int =None, sounds_page: int =1,
                maps_per_page: int =1, maps_page: int =None,
                texts_per_page: int =1, texts_page: int =1,
                subjects: List[str] =('overview',), licenses: List[str] =('all',), details: bool =False,
                common_names: bool =False, synonyms: bool =False, references: bool =False, taxonomy: bool =False,
                vetted: int =None, cache_ttl: int =None, language: str ='en') -> AttrDict:
    """This method takes an EOL page identifier and returns the scientific name for that page,
    and optionally returns information about common names, media (text, images and videos),
    and references to the hierarchies which recognize the taxon described on the page.

    Parameters
    ----------
    id
        EOL page identifier
    limit
        the number of item you want to get
    batch
        returns either a batch or not
    images_per_page : int of 0-75
        limits the number of returned objects
    images_page
        images page
    videos_per_page : int of 0-75
        limits the number of returned objects
    videos_page
        videos per page : int of 0-75
    sounds_per_page
        limits the number of returned objects
    sounds_page
        sounds per page : int of 0-75
    maps_per_page
        limits the number of returned objects
    maps_page
        maps per page : int of 0-75
    texts_per_page
        limits the number of returned objects
    texts_page
        texts per page : int of 0-75
    subjects
        'overview' to return the overview text (if exists), list of subject names from the list of
        EOL accepted subjects (e.g. TaxonBiology, FossilHistory), or 'all' to get text in any subject.
        Always returns an overview text as a first result (if one exists in the given context).
    licenses : str in ['cc-by', 'cc-by-nc', 'cc-by-sa', 'cc-by-nc-sa', 'pd', 'na', 'all']
        list of licenses or 'all' to get objects under any license.
        Licenses abbreviated cc- are all Creative Commons licenses.
        Visit their site for more information on the various licenses they offer.
        na for 'not applicable', and pd for public domain.
    details
        include all metadata for data objects
    common_names
        return all common names for the page's taxon
    synonyms
        return all synonyms for the page's taxon
    references
        return all references for the page's taxon
    taxonomy
        return any taxonomy details from different taxon hierarchy providers, in an array named "taxonConcepts"
    vetted
        If 'vetted' is given a value of '1', then only trusted content will be returned.
        If 'vetted' is '2', then only trusted and unreviewed content will be returned (untrusted content will not be returned).
        If 'vetted' is '3', then only unreviewed content will be returned.
        If 'vetted' is '4', then only untrusted content will be returned.The default is to return all content.
    cache_ttl
        the number of seconds you wish to have the response cached
    language : str in ['ms', 'de', 'en', 'es', 'fr', 'gl', 'it', 'nl', 'nb', 'oc',
    'pt-BR', 'sv', 'tl', 'mk', 'sr', 'uk', 'ar', 'zh-Hans', 'zh-Hant', 'ko']
        provides the results in the specified language

    Returns
    -------
    AttrDict
        example: {
            "identifier": 46559121,
            "scientificName": "Lutra lutra (Linnaeus, 1758)",
            "richness_score": null,
            "taxonConcepts": [
                {
                    "identifier": 2734123,
                    "scientificName": "Lutra lutra",
                    "name": "Lutra lutra",
                    "nameAccordingTo": "Flickr BHL",
                    "canonicalForm": "<i>Lutra lutra</i>",
                    "sourceIdentifier": "603dd500f57434c8532c8e97fd1da8f1"
                }, ...
            ],
            "dataObjects": [
                {
                    "identifier": "EOL-media-18-https://www.inaturalist.org/photos/1078195",
                    "dataObjectVersionID": 3760237,
                    "dataType": "http://purl.org/dc/dcmitype/StillImage",
                    "dataSubtype": "jpg",
                    "vettedStatus": "Trusted",
                    "dataRatings": [],
                    "dataRating": "2.5",
                    "mimeType": "image/jpeg",
                    "height": "2048",
                    "width": "1536",
                    "created": "2018-03-15T09:43:46.000Z",
                    "modified": "2018-10-19T18:57:16.000Z",
                    "license": "http://creativecommons.org/licenses/by-nc/4.0/",
                    "license_id": 7,
                    "rightsHolder": "Duarte Frade",
                    "source": "https://www.inaturalist.org/photos/1078195",
                    "mediaURL": "https://static.inaturalist.org/photos/1078195/original.JPG?1409230614",
                    "description": "Sorry about the terrible photos, but they were taken from afar and I didn't have much time to aim, since it submerged quickly.",
                    "eolMediaURL": "https://content.eol.org/data/media/28/6a/f2/18.https___www_inaturalist_org_photos_1078195.jpg",
                    "eolThumbnailURL": "https://content.eol.org/data/media/28/6a/f2/18.https___www_inaturalist_org_photos_1078195.98x68.jpg",
                    "agents": [
                        {
                        "full_name": "iNaturalist",
                        "homepage": null,
                        "role": "provider"
                        }
                    ]
                }, ...
            ]
        }
    """
    kwargs = deepcopy(locals())
    url = base_url.with_path(f'/api/pages/1.0/{id}.json')

    for k in [k for k in kwargs]:
        if kwargs[k] is None or k in ['limit', 'id']:
            del kwargs[k]
        elif k in ['subjects', 'licenses']:
            kwargs[k] = '|'.join(kwargs[k])
        elif not isinstance(kwargs[k], str):
            kwargs[k] = str(kwargs[k]).lower()
    url = url.with_query(**kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            # data returns in these styles:
            # Style 1: data == { "46559121": {...} }
            # Style 2: data == { "taxonConcept": {...} }
            for k in data:
                return AttrDict(data[k])


if __name__ == '__main__':
    import asyncio
    from pprint import pprint
    pprint(asyncio.run(pages(46559121, images_per_page=1, videos_per_page=0, maps_per_page=0, sounds_per_page=0,
                             texts_per_page=1, details=True, common_names=False, synonyms=False,
                             licenses=['cc-by', 'cc-by-nc', 'cc-by-sa', 'cc-by-nc-sa', 'pd'])))
