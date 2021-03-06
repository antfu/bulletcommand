import inspect
import time
import types
import sys
import traceback

from threading import Thread
from pprint import pprint

import pushbullet
from pushbullet import Pushbullet
from .push import Push
from .errors import *

class BotbulletThread(Thread):

    def __init__(self, switch=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.switch = switch

    def stop(self):
        self.switch[0] = False

    def __repr__(self):
        return '<BotbulletThread({})>'.format('Alive' if self.switch[0] else 'Stopped')


class Botbullet(Pushbullet):

    def __init__(self, *args, modified_after=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.listening_thread = None
        self.modified_after = modified_after or time.time()

    @staticmethod
    def _recipient(device=None, chat=None, email=None, channel=None, source_device=None):
        data = dict()

        if device:
            data["device_iden"] = device.device_iden
        elif chat:
            data["email"] = chat.email
        elif email:
            data["email"] = email
        elif channel:
            data["channel_tag"] = channel.channel_tag
        if source_device:
            data["source_device_iden"] = source_device.device_iden

        return data

    def push_note(self, title, body, device=None, chat=None, email=None, channel=None, source_device=None):
        data = {"type": "note", "title": title, "body": body}

        data.update(Botbullet._recipient(device, chat, email, channel, source_device))

        return self._push(data)

    def get_device_by_iden(self, device_iden):
        for device in self.devices:
            if device.device_iden == device_iden:
                return device
        return None

    def get_or_create_device(self, name):
        try:
            return self.get_device(name)
        except pushbullet.InvalidKeyError:
            return self.new_device(name)

    def listen_pushes(self, callback=None, modified_after=None, filter=None, sleep_interval=2, switch=None, log=None, debug=False):
        def noop(*args):
            pass

        log = log or print
        callback = callback or noop
        # This allows stopping listening from outer scope
        switch = switch or [True]

        debug and log('Pushes listening Start.')
        while True:
            try:
                pushes = self.get_pushes(modified_after=self.modified_after)
                if filter:
                    pushes = filter(pushes)
                if len(pushes):
                    length = len(pushes)
                    debug and log('{} pushes received.'.format(length))
                    for i in range(length):
                        callback(Push(pushes[i], self))
                    self.modified_after = pushes[-1].get('modified', None) or time.time()
                if not switch[0]:
                    debug and log('Pushes listening end.')
                    return
            except:
                if debug:
                    traceback.print_exc(file=sys.stdout)
            time.sleep(sleep_interval)

    def listen_pushes_asynchronously(self, *args, **kwargs):
        switch = [True]

        kwargs['switch'] = switch
        thread = BotbulletThread(switch=switch, target=self.listen_pushes, args=args, kwargs=kwargs)

        if self.listening_thread and self.listening_thread.is_alive():
            raise ThreadAlreadyExistsError('Thread already exists. You may want to execute "stop_listening" first.')
        self.listening_thread = thread
        thread.start()
        return thread

    def stop_listening(self):
        if self.listening_thread:
            if self.listening_thread.is_alive():
                self.listening_thread.stop()
            self.listen_threads = None

    def __del__(self):
        self.stop_listening()
