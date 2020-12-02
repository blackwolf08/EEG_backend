import asyncio
import datetime
import random
import websockets
import random
import json


HOST_ADDRESS = "127.0.0.1"
PORT = 5000

def generated_json():
    eeg_signal_list = random.sample(range(-127, 127), 10) #return []
    extra_data = {"is_epilepsy_detected":False}
    return {"eeg_signal_list":eeg_signal_list, "extra_data":extra_data}


async def get_eeg_json(websocket, path):
    while True:
        res = json.dumps(generated_json())
        await websocket.send(res)
        await asyncio.sleep(1)

start_server = websockets.serve(get_eeg_json, HOST_ADDRESS, PORT)
print(f"Server started on PORT {PORT}")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()