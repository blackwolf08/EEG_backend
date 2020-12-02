import asyncio
import datetime
import random
import websockets
import random
import json
import numpy as np
import os
PORT = os.environ.get('PORT', 5000)


import pickle
from sklearn.preprocessing import StandardScaler
scaler = pickle.load(open('scaler.sav', 'rb'))

loaded_model = pickle.load(open("pima.pickle.dat", "rb"))



HOST_ADDRESS = "0.0.0.0"
# HOST_ADDRESS = "127.0.0.1"
# PORT = 5000

eeg_signal = [ 512,  525,  525,  422,  322,  191,   89,  -13, -102, -163, -198,
       -199, -171, -140, -147, -138, -151, -205, -311, -449, -477, -453,
       -263,  -85,  101,  254,  336,  385,  370,  363,  361,  372,  384,
        365,  315,  230,  108,  -17, -143, -245, -318, -388, -428, -439,
       -435, -400, -402, -379, -333, -221,  -95,   30,   72,   58,   -5,
         15,   52,  137,  220,  277,  353,  388,  351,  282,  186,  113,
         70,   62,   75,   81,   65,   46,   32,    1,  -56, -118, -109,
       -114,  -79,  -40,  -35,  -43,  -75, -138, -235, -363, -485, -604,
       -582, -500, -328, -143,  -14,   84,  103,  105,  123,  191,  256,
        313,  357,  418,  468,  455,  402,  301,  198,   84,  -37, -129,
       -156, -185, -216, -220, -298, -313, -336, -277, -181, -148, -127,
       -129, -124, -163, -230, -340, -342, -304, -156,   20,  202,  351,
        439,  446,  382,  271,  152,   33,  -52, -147, -239, -312, -323,
       -287, -156,  -40,   72,  145,  143,  110,   31,   -4,  -32,  -48,
        -47,  -66,  -56,  -79, -131, -235, -351, -439, -414, -315, -130,
         44,  205,  291,  320,  302,  270,  209,  163,  131,  121,  109,
         78,   50]

start = 0
end = 30
result = False

def generated_json():
    global start
    global end
    global result
    eeg_signal_list =  eeg_signal[start:end]
    start += 1
    end += 1
    if end > len(eeg_signal):
        start = 0
        end = 30
        test = scaler.transform(np.array([eeg_signal]))
        if loaded_model.predict(np.array(test))[0] == 0:
            result = False
        else:
            result = True
    extra_data = {"is_epilepsy_detected":result}
    return {"eeg_signal_list":eeg_signal_list, "extra_data":extra_data}


async def get_eeg_json(websocket, path):
    while True:
        res = json.dumps(generated_json())
        await websocket.send(res)
        await asyncio.sleep(0.1)

start_server = websockets.serve(get_eeg_json, HOST_ADDRESS, PORT)
print(f"Server started on PORT {PORT}")

generated_json()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()