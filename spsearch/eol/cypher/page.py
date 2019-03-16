from typing import Union, List, TYPE_CHECKING
import textwrap
from .core import CypherExecutor
from .trait import TraitProxy, Trait


class Page:
    def __init__(self, executor: CypherExecutor =None, data: dict =None, canonical =None, page_id =None, token: str =None):
        assert executor or token, 'Either executor or token should be given'
        assert data or canonical or page_id, 'Either data, canonical or page_id has to be given'
        self._data = data
        self.executor = executor if isinstance(executor, CypherExecutor) else CypherExecutor(token)
        self.canonical = data.get('canonical') if data else canonical
        self.page_id = data.get('page_id') if data else page_id

        # page_id か canonical のどっちか存在する方を Page の指定子として使う
        self._identifier = f'{{page_id: {self.page_id}}}' if self.page_id else f'{{canonical: "{self.canonical}"}}'

    @property
    def name(self):
        return self.canonical

    @property
    def id(self):
        return self.page_id

    @classmethod
    async def from_id(cls, executor: CypherExecutor, id: Union[int, str]) -> 'Page':
        result = await executor.execute(textwrap.dedent(f'''
            MATCH (p:Page {{page_id: {id} }})
            RETURN properties(p)
        '''))
        return cls(executor, canonical=result['data']['canonical'],
                   page_id=result['data']['canonical'])

    @classmethod
    async def from_name(cls, executor: CypherExecutor, name: str) -> 'Page':
        result = await executor.execute(textwrap.dedent(f'''
            MATCH (p:Page {{canonical: "{name}" }})
            RETURN properties(p)
        '''))
        print(result)
        return cls(executor, canonical=result['data'][0][0]['canonical'],
                   page_id=result['data'][0][0]['page_id'])

    def __str__(self):
        return self.canonical

    def __repr__(self):
        return f'<Page canonical="{self.canonical}", page_id="{self.page_id}">'

    async def get_categories(self) -> List[TraitProxy]:
        """Gets list of available categories (or predicates)"""
        query = textwrap.dedent(f'''
            MATCH (p:Page {self._identifier})-[:trait]->(t:Trait)-[:predicate]->(pred:Term)
            RETURN COLLECT(DISTINCT [pred.uri, pred.name])
        ''')
        result = await self.executor.execute(query)
        return [TraitProxy(uri=i[0], name=i[1]) for i in result['data'][0][0]]

    async def get_traits(self, category: Union[str, TraitProxy] =None) -> List[Trait]:
        where = ''
        if category:
            where = f'WHERE pred.name = "{category}"'\
                    + (f' and pred.uri = "{category.uri}"' if isinstance(category, TraitProxy) else '')

        query = textwrap.dedent(f'''
            MATCH (p:Page {self._identifier})-[:trait]->(t:Trait),
                  (t)-[:supplier]->(r:Resource),
                  (t)-[:predicate]->(pred:Term)
            {where}
            OPTIONAL MATCH (t)-[:object_term]->(obj:Term)
            OPTIONAL MATCH (t)-[:normal_units_term]->(units:Term)
            OPTIONAL MATCH (lit:Term) WHERE lit.uri = t.literal
            RETURN properties(p), properties(t), properties(r), properties(pred), properties(obj), properties(units), properties(lit)
        ''')
        result = await self.executor.execute(query)
        return [Trait(self.executor, Page(self.executor, data=datum[0]), datum[1], datum[2], datum[3],
                      datum[4], datum[5], datum[6]) for datum in result['data']]
