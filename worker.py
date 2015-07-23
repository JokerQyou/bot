# coding: utf-8
from os import path
import sys

import json
from redis import Redis
from rq import Worker, Queue, Connection

__dirname__ = path.dirname(__file__)
__config__ = 'config.json'

sys.path.insert(0, path.abspath(__dirname__))
sys.path.insert(0, path.abspath(path.join(__dirname__, 'botcommands')))

redis_config = {}

with open(__config__, 'r') as crf:
    redis_config = json.loads(crf.read()).get('redis')


def main():
    global redis_config
    not redis_config and sys.exit('Missing redis config')
    listen = ('high', 'default', 'low', )
    conn = Redis(**redis_config)
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()

if __name__ == '__main__':
    main()
