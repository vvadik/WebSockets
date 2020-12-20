#!/usr/bin/env python3

import re
from aiohttp import web


class WSChat:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.conns = {}
        self.commands = {'INIT': self.init,
                         'TEXT': self.text}
        self.dels = []

    async def main_page(self, request):
        return web.FileResponse('./index.html')

    def run(self):
        app = web.Application()
        app.router.add_get('/', self.main_page)
        app.router.add_get('/chat', self.get)
        web.run_app(app, host=self.host, port=self.port)

    async def get(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            await self.cleanup()

            if msg[1] != 'ping':
                print(msg)
                print(msg[1], type(msg[1]))

            if msg[1] == 'ping':
                await ws.send_str('pong')
            else:
                type_ = re.findall(r'"mtype":"(.+?)"', msg[1])[0]
                print(type_)
                await self.commands[type_](ws, msg[1])

    async def send_all(self, id, type, msg='', receiver=''):
        for client, ws in self.conns.items():
            try:
                if id != client:
                    if type == 'user_in':
                        await ws.send_json({'mtype': 'USER_ENTER', 'id': id})

                    elif type == 'user_out':
                        await ws.send_json({'mtype': 'USER_LEAVE', 'id': id})

                    elif type == 'msg_all':
                        await ws.send_json({'mtype': 'MSG', 'id': id,
                                            'text': msg})

                    elif type == 'msg_to':
                        await ws.send_json({'mtype': 'DM', 'id': id,
                                            'text': msg})
            except ConnectionResetError:
                # delete inactive
                self.dels.append(client)

    async def init(self, ws, msg):
        client = re.findall(r'"id":"(.+?)"', msg)[0]
        self.conns[client] = ws
        print(self.conns)
        await self.send_all(client, 'user_in')

    async def text(self, ws, msg):
        client = re.findall(r'"id":"(.+?)"', msg)[0]
        receiver = re.findall(r'"to":(.+?),', msg)[0]
        text = re.findall(r'"text":"(.+?)"}', msg)[0]

    async def cleanup(self):
        # unsafe??? idk
        for i in self.dels:
            await self.send_all(i, 'user_out')
            del self.conns[i]
        self.dels = []


if __name__ == '__main__':
    WSChat().run()
