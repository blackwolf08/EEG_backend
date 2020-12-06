import asyncio
import datetime
import random
import websockets
import random
import json
import numpy as np
import person1, person2
import os
PORT = os.environ.get('PORT', 5000)


import pickle
from sklearn.preprocessing import StandardScaler
scaler = pickle.load(open('scaler.sav', 'rb'))

loaded_model = pickle.load(open("pima.pickle.dat", "rb"))


# from twilio.rest import Client

# account_sid = "ACae3514f541d5877b687ae3d5566eda99"
# auth_token  = "9667a5dbfca7654c18505ce2e58b78de"

# client = Client(account_sid, auth_token)

messageSent = False

# def sendMessage() :
#     print('sending message')
#     message = client.messages.create(
#             to= '+919958470889',
#             from_= '+19183794343',
#             body= 'Yahan mara padha hun mein bsdk!'
#         )
#     print(message.sid)


HOST_ADDRESS = "0.0.0.0"
# HOST_ADDRESS = "127.0.0.1"


GRAPH_DATA_RATE = 0.1 # in seconds

start = 0
end = 30
result = False

sending_data = person2.eeg_signal


STATE = {
    'which' : 1
}


def generated_json():
    global start
    global end
    global result
    global messageSent
    
    eeg_signal_list = sending_data[start:end]
    start += 1
    end += 1
    if end > len(sending_data):
        start = 0
        end = 30
        test = scaler.transform(np.array([sending_data]))
        if loaded_model.predict(np.array(test))[0] == 0:
            result = False
        else:
            result = True
            if not messageSent:
                messageSent = True
                sendMessage()
    extra_data = {"is_epilepsy_detected":result}
    return {"eeg_signal_list":eeg_signal_list, "extra_data":extra_data}

async def set_state(websocket):
    global STATE
    async for msg in websocket:
        if(msg == 'two'):
            STATE['which'] = 2
            messageSent = False
            sending_data = person1.eeg_signal
        if(msg == 'one'):
            STATE['which'] = 1
            messageSent = False
            sending_data = person2.eeg_signal
        start = 0
        end = 30


async def send_data(websocket):
    while True:
        res = json.dumps(generated_json())
        await websocket.send(res)
        await asyncio.sleep(0.1)
    

async def get_eeg_json(websocket, path):
    send_eeg_data_to_client = asyncio.ensure_future(
        send_data(websocket))
    listen_for_changes_from_client = asyncio.ensure_future(
        set_state(websocket))
    done, pending = await asyncio.wait(
        [send_eeg_data_to_client, listen_for_changes_from_client],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    

start_server = websockets.serve(get_eeg_json, HOST_ADDRESS, PORT)
print(f"Server started on PORT {PORT}")

generated_json()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()