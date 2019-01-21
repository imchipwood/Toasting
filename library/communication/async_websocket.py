import asyncio
import websockets
import json

# https://stackoverflow.com/questions/45002490/how-to-receive-data-from-web-sockets-using-python


async def hello(websocket, path):
	data = await websocket.recv()
	data = json.loads(data)
	print(json.dumps(data, indent=2))
	await websocket.send("message {} received".format(data.get('id', "NONE")))


HOST, PORT = 'localhost', 9999
start_server = websockets.serve(hello, HOST, PORT)

try:
	asyncio.get_event_loop().run_until_complete(start_server)
	asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
	print("Shutting down event loop")
	asyncio.get_event_loop().stop()
