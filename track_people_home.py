import threading
import json
import asyncio

import websockets

from helpers import *


WEBSOCKET_PORT = 6201
addresses = {
    'Maria': '192.168.86.95', # "Maria-Pixel"
    'Eric': '192.168.86.46', # something like "eric-pixel"
    'Andrew': '192.168.86.45', # i think "android-2"
    'Matt': '192.168.86.87', # i think "Android"
    'Randy': '192.168.86.37', # i think "Pixel-5a"
    'Mary': '192.168.86.49', # i think "Android-2"
    'Chris': None,
}

state = {person:{'home': True, 'stake_balance': None} for person in addresses}
def is_alive(ip_addr):
    for _ in range(3):
        retcode, stdout, stderr = run_command_blocking([
            'fping',
            f'-t20000',
            f'-c1',
            f'{ip_addr}',
        ]) # t is milliseconds, c is number of retries
        if retcode == 0:
            return True
    return False


send_update = False
def track_person(person, ip_addr):
    global send_update
    while True:
        if ip_addr is not None:
            new_reading = is_alive(ip_addr)
            if new_reading != state[person]['home']:
                send_update = True
            state[person]['home'] = new_reading
            if state[person]['home']:
                print_green(f'{person} is home')
            else:
                print_red(f'{person} is NOT home')
            time.sleep(15)


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
    global state
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

        if 'stake_balance' in msg and 'person' in msg:
            person = msg['person']
            stake_balance = msg['stake_balance']
            print(f'Updating stake balance for {person} to {stake_balance}')
            state[person]['stake_balance'] = stake_balance

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