import threading
import json
import asyncio

import websockets

from helpers import *


WEBSOCKET_PORT = 6201
addresses = {
    'Maria': '192.168.86.29', # something like "maria-pixel"
    'Eric': '192.168.86.46', # something like "eric-pixel"
    'Andrew': '192.168.86.45', # i think "android-2"
    'Matt': '192.168.86.87', # i think "Android"
    'Randy': '192.168.86.37', # i think "Pixel-5a"
}

state = {person:True for person in addresses}
def is_alive(ip_addr):
    retcode, stdout, stderr = run_command_blocking([
        'fping',
        f'-t40000',
        f'-c1',
        f'{ip_addr}',
    ]) # t is milliseconds, c is number of retries
    return retcode == 0


send_update = False
def track_person(person, ip_addr):
    global send_update
    while True:
        new = is_alive(ip_addr)
        if new != state[person]:
            send_update = True
        state[person] = new
        if state[person]:
            print_green(f'{person} is home')
        else:
            print_red(f'{person} is NOT home')
        time.sleep(7)

async def broadcast(msg):
    for socket in sockets:
        try:
            print_green(f'Sending to socket: {socket}')
            await socket.send(msg)
            print_green(f'sent to socket: {socket}')
            return True
        except:
            print(f'socket send failed. socket: {socket}', flush=True)


sockets = []
async def init_client(websocket, path):
    try:
        print(f'Trying to send first message to client: {websocket}')
        await websocket.send(json.dumps(state))
        print(f'sent first message to client: {websocket}')
    except:
        return print_red('client send failed')

    sockets.append(websocket)
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


async def send_updates_infinite():
    global send_update
    while True:
        if send_update:
            await broadcast(json.dumps(state))
            send_update = False
        await asyncio.sleep(1)


async def start_async():
    server = await websockets.serve(init_client, '0.0.0.0', WEBSOCKET_PORT)
    asyncio.create_task(send_updates_infinite())
    await server.serve_forever()

threads = []
for person, ip_addr in addresses.items():
    threads.append(threading.Thread(target=track_person, args=(person, ip_addr)))
    threads[-1].start()

asyncio.run(start_async())