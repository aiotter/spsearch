from spsearch.eol import CypherExecutor
import typing
import textwrap
from spsearch.classes import AttrDict, AttrSeq
from pprint import pprint
from pathlib import Path

assert Path('.token').exists(), "token has to be stored at ./.token"


async def test():
    query = textwrap.dedent('''
        MATCH (p:Page {page_id: 46559121})-[:trait]->(t:Trait),
              (t)-[:supplier]->(r:Resource),
              (t)-[:predicate]->(pred:Term)
        OPTIONAL MATCH (t)-[:object_term]->(obj:Term)
        OPTIONAL MATCH (t)-[:normal_units_term]->(units:Term)
        OPTIONAL MATCH (lit:Term) WHERE lit.uri = t.literal
        RETURN properties(p), properties(t), properties(r), properties(pred), properties(units), properties(lit)
        LIMIT 10
    ''')
    with open('.token', 'r', encoding='utf-8') as token:
        cypher = CypherExecutor(token)
        pprint(await cypher.execute(query))


async def test2(page_id: typing.Union[int, str], **kwargs):
    where = " AND ".join(f'pred.{k} = "{v}"' for (k, v) in kwargs.items())
    query = textwrap.dedent(f'''
        MATCH (p:Page {{page_id: {page_id} }})-[:trait]->(t:Trait),
              (t)-[:supplier]->(r:Resource),
              (t)-[:predicate]->(pred:Term)
        {f"WHERE {where}" if where else ""}
        OPTIONAL MATCH (t)-[:object_term]->(obj:Term)
        OPTIONAL MATCH (t)-[:normal_units_term]->(units:Term)
        OPTIONAL MATCH (lit:Term) WHERE lit.uri = t.literal
        RETURN properties(p), properties(t), properties(r), properties(pred), properties(units), properties(lit)
    ''')
    with open('.token', 'r', encoding='utf-8') as token:
        cypher = CypherExecutor(token)
    result = await cypher.execute(query)
    return AttrSeq(
        {
            'page': datum[0],
            'trait': datum[1],
            'resource': datum[2],
            'predicate': datum[3],
            'units': datum[4],
            'literal': datum[5],
        } for datum in result['data']
    )


async def available_for(page_id: typing.Union[int, str]) -> list:
    query = textwrap.dedent(f'''
        MATCH (p:Page {{page_id: {page_id}}})-[:trait]->(t:Trait)-[:predicate]->(pred:Term)
        RETURN COLLECT(DISTINCT [pred.uri, pred.name])
        LIMIT 1
    ''')
    with open('.token', 'r', encoding='utf-8') as token:
        cypher = CypherExecutor(token)
    result = await cypher.execute(query)
    return [(i[0], i[1]) for i in result['data'][0][0]]


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    # result = loop.run_until_complete(test())
    # result = loop.run_until_complete(available(46559121))
    results = loop.run_until_complete(test2(46559121, name="habitat includes"))

    """
    from pprint import pprint
    result = FrozenList([{"a": 0, "b": 1}, {"c": 2}, {"d": 3}])
    print(result)
    print(type(result))
    print(result[0])
    print(type(result[0]))
    """

    pprint({str(r.keys()) for r in results})
    print(results[0].predicate.definition)
