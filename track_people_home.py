import threading
import json
import asyncio
import http.server
import socket

import websockets

from helpers import *


WEBSOCKET_PORT = 6101
SOCKET_PORT = 6102



addresses = {
    'maria': '192.168.86.29',
    'eric': '192.168.86.46',
}

state = {person:True for person in addresses}
def is_alive(ip_addr):
    return subprocess.call(['fping', '-t10000', '-c1', ip_addr]) == 0 # t is milliseconds


def track_whos_home():
    while True:
        for person, ip_addr in addresses.items():
            state[person] = is_alive(ip_addr)
        time.sleep(1)


async def broadcast(msg):
    for socket in sockets:
        try:
            await socket.send(msg)
            return True
        except:
            print(f'socket send failed. socket: {socket}', flush=True)


sockets = []
async def init_client(websocket, path):
    sockets.append(websocket)
    if not broadcast(json.dumps(state)):
        return sockets.remove(websocket)

    while True:
        try:
            msg_string = await websocket.recv()
        except:
            sockets.remove(websocket)
            print('socket recv FAILED - ' + websocket.remote_address[0] + ' : ' + str(websocket.remote_address[1]), flush=True)
            break

        try:
            msg = json.loads(msg_string)
        except:
            print('NOT JSON: SKIP')
            print(f'msg string: {msg_string}', flush=True)
            continue

        print('message recieved: ', msg)
        await broadcast(json.dumps(state))

if is_andrewpi():
    local_ip = '192.168.86.84'
else:
    local_ip = 'UNKNOWN_IP'
try:
    info = socket.gethostbyname_ex(socket.gethostname())
    if '127.0.1' not in info[2][0]:
        local_ip = info[2][0]
    else:
        print_yellow('warning, failed to gethostbyname_ex accurately, ip could be wrong')
except:
    pass

async def start_async():
    server = await websockets.serve(init_client, '0.0.0.0', WEBSOCKET_PORT)
    await server.serve_forever()

threading.Thread(target=track_whos_home).start()

asyncio.run(start_async())