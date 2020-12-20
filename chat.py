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
            if msg[1] != 'ping':
                print(msg)
                print(msg[1], type(msg[1]))

            if msg[1] == 'ping':
                await ws.send_str('pong')
            else:
                type_ = re.findall(r'"mtype":"(.+?)"', msg[1])[0]
                await self.commands[type_](ws, msg[1])

        await self.send_all(self.conns[ws], 'user_out')
        del self.conns[ws]

    async def send_all(self, id, type_, msg='', receiver=''):
        for ws, client in self.conns.items():
            if id != client:
                print(client, type(client), receiver, type(receiver))
                if type_ == 'user_in':
                    await ws.send_json({'mtype': 'USER_ENTER', 'id': id})

                elif type_ == 'user_out':
                    await ws.send_json({'mtype': 'USER_LEAVE', 'id': id})

                elif type_ == 'msg_all':
                    await ws.send_json({'mtype': 'MSG', 'id': id,
                                        'text': msg})

                elif type_ == 'msg_to' and receiver == client:
                    await ws.send_json({'mtype': 'DM', 'id': id,
                                        'text': msg})

    async def init(self, ws, msg):
        client = re.findall(r'"id":"(.+?)"', msg)[0]
        self.conns[ws] = client
        await self.send_all(client, 'user_in')

    async def text(self, ws, msg):
        client = re.findall(r'"id":"(.+?)"', msg)[0]
        receiver = re.findall(r'"to":"?(.+?)"?,', msg)[0]
        text = re.findall(r'"text":"(.+?)"}', msg)[0]
        if receiver == 'null':
            await self.send_all(client, 'msg_all', text)
        else:
            await self.send_all(client, 'msg_to', text, receiver)


if __name__ == '__main__':
    WSChat().run()
