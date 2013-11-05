#!/usr/bin/env python3

import json
import signal
import subprocess
import urllib.request

from os.path import expanduser
from os.path import join as join_path


def get_streams_json(url='http://listen.di.fm/public3'):
    response = urllib.request.urlopen(url)
    unsorted = json.loads(response.read().decode('utf8'))
    return sorted(unsorted, key=lambda stream: stream['name'])


def get_valid_stream_ndx(max_ndx, default=0):
    while(True):
        prompt = "\nSelect a radio station (default {}) => "
        select = input(prompt.format(default))
        try:
            select = int(select)
        except ValueError:
            if select == '':
                return default
            continue

        if 0 <= select <= max_ndx:
            return select


def play_stream(stream, player='mpv', use_cache=True, cache_size=1024):
    player_args = [player]
    if use_cache:
        player_args.extend(['-cache', '{}'.format(cache_size)])
    player_args.extend(['-playlist', stream['playlist']])
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    subprocess.call(player_args)
    signal.signal(signal.SIGINT, signal.SIG_DFL)


def write_last_channel(channel_id):
    with open(join_path(expanduser('~'), '.radio_last_chan'), "w+") as f:
        f.write("{}".format(channel_id))


def read_last_channel():
    last_chan = 0
    try:
        with open(join_path(expanduser('~'), '.radio_last_chan'), "r") as f:
            last_chan = f.read()
    except FileNotFoundError:
        pass

    return int(last_chan)


def get_channel_ndx_from_id(streams, _id, default=0):
    for ndx, stream in enumerate(streams):
        if stream['id'] == _id:
            return ndx

    return default


def max_channame_len(streams):
    max_name_len = 0
    for stream in streams:
            max_name_len = max(len(stream['name']), max_name_len)

    return max_name_len


if __name__ == "__main__":
    while(True):
        streams = get_streams_json()
        max_name_len = max_channame_len(streams)
        for ndx, stream in enumerate(streams):
            print("[{0:>3}] {1: <{2}} - {3}".format(ndx,
                                                    stream['name'],
                                                    max_name_len,
                                                    stream['description']))

        last_stream_ndx = get_channel_ndx_from_id(streams, read_last_channel())
        selection = get_valid_stream_ndx(len(streams)-1,
                                         default=last_stream_ndx)
        play_stream(streams[selection])
        write_last_channel(streams[selection]['id'])

# vim: ts=8 sts=4 sw=4 et
