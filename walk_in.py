import subprocess
import time

from pydub import AudioSegment
from pydub.playback import play

from helpers import *

def ping(host):
    print(f'pinging {host}')
    # t is milliseconds
    return subprocess.call(['fping', '-t10000', '-c1', host]) == 0


addresses = {
    # 'maria': '192.168.86.29',
    'eric': '192.168.86.46',
}
# yt-dlp -f "bestaudio" -x "https://www.youtube.com/watch?v=-cHOIMi8__o" --extract-audio --audio-format wav


walk_ins = {
    'maria': 'youtube',
    'eric': 'songs/make_it_forever.wav',
}

last = {person:True for person in addresses}

while True:
    for person, ip_addr in addresses.items():
        result = ping(ip_addr)
        if result:
            print_green(f'pinged {person} and success')
            if not last[person]:
                print('playing')
                song = AudioSegment.from_wav("sound.wav")
                play(song)
        else:
            print_red(f'pinged {person} and failure')
        last[person] = result
    time.sleep(1)