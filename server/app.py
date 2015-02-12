# encoding: utf-8
from __future__ import absolute_import, division, with_statement

from tornado import websocket, web, ioloop
from game.logic import Hub, Game, Player
from game.ai import AiPlayer, AiHandler
import json
import os
import config


class BaseGameController(object):

    def create_game(self, hub):
        Game(hub, {
            'fieldHeight': config.FIELD_HEIGHT,
            'fieldWidth': config.FIELD_WIDTH,
            'sidePadding': config.SIDE_PADDING,
            'topPadding': config.TOP_PADDING,
            'sideHeight': config.SIDE_HEIGHT,
            'sideWidth': config.SIDE_WIDTH,
            'ballRadius': config.BALL_RADIUS,
            'ballMinSpeed': config.BALL_MIN_SPEED,
            'ballMaxSpeed': config.BALL_MAX_SPEED
        }, ioloop.IOLoop.instance())


class SinglePlayerController(BaseGameController):

    def handle_player(self, new_player):
        hub = Hub()
        hub.add_player(AiPlayer(AiHandler()))
        hub.add_player(new_player)
        self.create_game(hub)


class MultiPlayerController(BaseGameController):

    def __init__(self, *args, **kwargs):
        super(MultiPlayerController, self).__init__(*args, **kwargs)
        self.hubs = []

    def handle_player(self, new_player):
        hub = self.get_free_hub()
        if not hub.is_full():
            hub.add_player(new_player)

        # print os.getpid()
        # print len(hub.players)
        
        # wait player or create game if is last player then run game
        if hub.is_ready_to_play():
            self.create_game(hub)

    def get_free_hub(self):
        for hub in self.hubs:
            if not hub.is_full():
                return hub
        hub = Hub()
        self.hubs.append(hub)
        return hub


multiplayer_controller = MultiPlayerController()
singleplayer_controller = SinglePlayerController()


class Handler(websocket.WebSocketHandler):

    def open(self):
        self.player = Player(self)
        if config.GAME_TYPE == 'singleplayer':
            singleplayer_controller.handle_player(self.player)
        elif config.GAME_TYPE == 'multiplayer':
            multiplayer_controller.handle_player(self.player)
        else:
            raise Exception('Unknown game type')

    def write_message(self, message, binary=False):
        if not binary:
            message = json.dumps(message)
        super(Handler, self).write_message(message, binary)

    def on_message(self, message):
        if self.player.in_game:
            message = json.loads(message)
            self.player.game.on_player_message(message, self.player)

    def check_origin(self, origin):
        return True

class CustomApplication(web.Application):
    def start(self, port):
        from tornado.httpserver import HTTPServer
        server = HTTPServer(self)
        server.bind(port)
        server.start(config.WORKERS_SPAWN)

app = CustomApplication([
        (r'/game', Handler)
    ])

if __name__ == '__main__':
    app.start(config.LISTEN_PORT)
    ioloop.IOLoop.instance().start()



