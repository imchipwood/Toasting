import asyncio
import websockets
import json

from definitions import GetBaseConfigurationFilePath
from library.control.stateMachine import ToastStateMachine

model = ToastStateMachine(jsonConfigPath=GetBaseConfigurationFilePath())

# https://stackoverflow.com/questions/45002490/how-to-receive-data-from-web-sockets-using-python


def get_flattened_tuning():
	config = model.config
	return {
		'kP': config.pids.kP,
		'kI': config.pids.kI,
		'kD': config.pids.kD,
		'outputMin': config.pids.min,
		'outputMax': config.pids.max,
		'windupGuard': config.pids.windupGuard,
		'timerPeriod': config.clockPeriod,
		'pinRelay': config.relayPin,
		'pinSpiCs': config.spiCsPin,
	}


async def hello(websocket, path):
	data = await websocket.recv()
	data = json.loads(data)
	message_id = data.get('id', 'NONE')
	message_type = data.get('type')
	message_method = data.get('method')
	message_text = data.get('text')
	print("{} {} of type {} received".format(message_method, message_id, message_type))
	print(json.dumps(message_text, indent=2))

	if message_method == 'GET':
		if message_type == 'tuning':
			msg = {
				'tuning': get_flattened_tuning(),
				'ACK': message_id
			}
			await websocket.send(json.dumps(msg))
	else:
		await websocket.send(json.dumps({'ACK': message_id}))


HOST, PORT = 'localhost', 9999
# HOST, PORT = 'localhost', 3000
start_server = websockets.serve(hello, HOST, PORT)

try:
	asyncio.get_event_loop().run_until_complete(start_server)
	asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
	print("Shutting down event loop")
	asyncio.get_event_loop().stop()
