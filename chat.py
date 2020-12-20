#!/usr/bin/env python3

import re
from aiohttp import web
# TODO


class WSChat:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.conns = {}
        self.clients = []

    async def main_page(self, request):
        return web.FileResponse('./index.html')

    # TODO

    def run(self):
        app = web.Application()
        app.router.add_get('/', self.main_page)
        app.router.add_get('/chat', self.get)
        web.run_app(app, host=self.host, port=self.port)

    async def get(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        print(request)

        async for msg in ws:
            print(msg)
            print(msg[1], type(msg[1]))
            if msg[1] == 'ping':
                await ws.send_str('pong')
            else:
                await self.parse(msg[1])
                # user enter the chat
                print('WE ARE HEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEERE')
                self.clients.append(msg[1][1])
                print(self.clients)
                await ws.send_json(f"'mtype': 'USER_ENTER', 'id': '{id}'")
                await self.send_all(ws, msg[1][1], 'service')
                # TODO: рассылка всем

    async def send_all(self, ws, id, type, msg=''):
        for client in self.clients:
            if id != client:
                if type == 'service':
                    ws.send_json(f"'mtype': 'USER_ENTER', 'id': '{id}'")
                elif type == 'msg_all':
                    ws.send_json(f"'mtype': 'MSG', 'id': '{id}', 'text': '{msg}'")

    async def parse(self, msg):
        type_ = re.findall(r'"mtype":"(.+?)"', msg)
        print(type_)







            # if msg.tp == MsgType.text:
            #     if msg.data == 'close':
            #         await ws.close()

        # async for msg in ws:
        #     if msg.tp == MsgType.text:
        #         if msg.data == 'close':
        #             await ws.close()
        #         else:
        #
        #             for _ws in self.request.app['websockets']:
        #                 _ws.send_str('(%s) %s' % (msg.data))
        #     elif msg.tp == MsgType.error:
        #         log.debug(
        #             'ws connection closed with exception %s' % ws.exception())
        #
        # self.request.app['websockets'].remove(ws)
        # for _ws in self.request.app['websockets']:
        #     _ws.send_str('%s disconected' % login)
        # log.debug('websocket connection closed')


if __name__ == '__main__':
    WSChat().run()
