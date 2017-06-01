from sanic import Sanic
import ssl
from sanic.response import json
import os
app = Sanic()

@app.route('/')
async def test(request):
  return json({'hello': 'world'})
  
@app.route('/tag/<tag>')
async def tag_handler(request, tag):
  return json({'tag': tag})

SSL= os.environ['SSL']

context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)

context.load_cert_chain(SSL + '/fullchain.pem', keyfile=SSL + '/privkey.pem')  
if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8000, ssl=context)