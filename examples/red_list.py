import asyncio
from biohub.redlist import RedListApiHandler

with open('.redlist.token', encoding='utf-8') as token:
    handler = RedListApiHandler(token)


async def info(name):
    global handler
    sp = await handler.species_from_name(name)
    print(sp)
    # print(sp.category)
    # pprint(sp.__dict__)
    pprint(await sp.get_habitats())


async def list_up(category):
    global handler
    species = await handler.species_from_category(category)
    pprint(species)


if __name__ == '__main__':
    from sys import argv
    from pprint import pprint

    loop = asyncio.get_event_loop()
    # loop.run_until_complete(info('Aonyx cinerea'))
    loop.run_until_complete(info(argv[1]))
    # loop.run_until_complete(list_up(argv[1]))
