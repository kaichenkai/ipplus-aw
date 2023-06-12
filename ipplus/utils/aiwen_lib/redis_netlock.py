# coding:utf-8
"""
this file copied from python package redis-netlock=1.6
because that package has some bugs, we maintain it outselves
"""
import time

from contextlib import contextmanager

DEFAULT_EXPIRES = 15
DEFAULT_RETRIES = 5


@contextmanager
def dist_lock(key, client):
    key = 'lock_%s' % key

    try:
        t = _acquire_lock(key, client)
        yield t
    finally:
        _release_lock(key, client)


def ask_lock(key, client):
    key = 'lock_%s' % key
    if client.get(key):
        return True
    else:
        return False


def _acquire_lock(key, client):
    for i in range(DEFAULT_RETRIES):
        ttl = client.ttl(key)
        if ttl == -2:
            if client.setnx(key, 1):
                client.expire(key, DEFAULT_EXPIRES)
                return True
        elif ttl == -1:
            client.expire(key, DEFAULT_EXPIRES)
            return False
        else:
            time.sleep(0.2)
    return False


def _release_lock(key, client):
    client.delete(key)
