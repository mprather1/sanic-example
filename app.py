from sanic import Sanic
import ssl
from sanic.response import json
import os
import asyncio
import aiopg
import uvloop

database_name = os.environ['DATABASE_NAME']
database_host = os.environ['DATABASE_HOST']
database_user = os.environ['DATABASE_USER']
database_password = os.environ['DATABASE_PASSWORD']

connection = 'postgres://{0}:{1}@{2}/{3}'.format(database_user,
                                                 database_password, 
                                                 database_host,
                                                 database_name)
                                                 
async def get_pool():
  return await aiopg.create_pool

app = Sanic()

@app.listener('before_server_start')
async def prepare_db(app, loop):
  """
  Create table and some data
  """
  async with aiopg.create_pool(connection) as pool:
    async with pool.acquire() as conn:
      async with conn.cursor() as cur:
        await cur.execute('DROP TABLE IF EXISTS sanic')
        await cur.execute("""CREATE TABLE sanic (
                             id serial primary key,
                             name varchar(50),
                             pub_date timestamp
                          );""")
                          
        for i in range(0, 100):
          await cur.execute("""INSERT INTO sanic
                             (id, name, pub_date) VALUES ({}, {}, now())
                            """.format(i, i))
                        
@app.route("/")
async def handle(request):
  result = []
  async def test_select():
    async with aiopg.create_pool(connection) as pool:
      async with pool.acquire() as conn:
        async with conn.cursor() as cur:
          await cur.execute('SELECT name, pub_date FROM sanic')
          async for row in cur:
            result.append({'name': row[0], 'pub_date': row[1]})
  res = await test_select()
  return json({'data': result})
  
SSL= os.environ['SSL']

context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)

context.load_cert_chain(SSL + '/fullchain.pem', keyfile=SSL + '/privkey.pem')  
if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8000, ssl=context, debug=True)