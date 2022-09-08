import aiohttp, asyncio, asyncpg, ssl
from dotenv import dotenv_values

async def get_items(page, api_key, sesh):
    resp = await sesh.get(f'https://api.barcodelookup.com/v3/products?category=Cosmetics&key={api_key}&page={page}')
    r_dict = await resp.json()
    return r_dict['products']

async def db_insert(item_page, conn):
    for item in item_page:
        async with conn.transaction():
            await conn.execute('''INSERT INTO ean13_products VALUES($1, $2, $3)
                ON CONFLICT ON CONSTRAINT ean13_products_pkey DO NOTHING;
                ''', item['barcode_number'], item['brand'], item['title'])

async def load_items(num_pages, env_file):
    conf = dotenv_values(env_file)
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=conf['CA_FILE'])
    ctx.check_hostname = False
    ctx.load_cert_chain(conf['CRT_FILE'], keyfile=conf['KEY_FILE'])
    conn = await asyncpg.connect(host=conf['HOST'], user=conf['USERNAME'], password=conf['DB_PASSWORD'], database=conf['DB_NAME'], ssl=ctx)
    try:
        async with aiohttp.ClientSession(raise_for_status=True) as client:
            tasks = [asyncio.ensure_future(get_items(i, conf['API_KEY'], client)) for i in range(1, num_pages+1)]
            for task in asyncio.as_completed(tasks):
                page = await task
                await db_insert(page, conn)
    finally:
        await conn.close()

# Uncomment before running on Windows
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(load_items(1, r'path/to/file'))