# encoding: utf-8

from __future__ import absolute_import, division, with_statement
from game.logic import Player

# fixme: Direct dependency
from tornado import ioloop
import datetime
import config

speed_dependency = {
    0: 0,
    4: 6,
    5: 7,
    6: 7,
    7: 8,
    8: 9,
    9: 9,
    10: 10,
    11: 10,
    12: 11
}


class AiPlayer(Player):

    def __init__(self, *args, **kwargs):
        super(AiPlayer, self).__init__(*args, **kwargs)
        self.ioloop = ioloop.IOLoop.instance()
        self.ai_interval = None

    def on_game_connected(self):
        self.ai_loop()

    def ai_loop(self):
        self.ai_logic()
        self.ai_interval = self.ioloop.add_timeout(datetime.timedelta(milliseconds=(1000/config.AI_ACTIVE_LOOP)), self.ai_loop)

    def ai_logic(self):
        ball = self.game.ball
        side = self.side
        vY = self.game.settings['ballMinSpeed']
        pY = 0
        borders = self.game.settings['topPadding']
        field_width = self.game.settings['fieldWidth']
        field_height = self.game.settings['fieldHeight']
        if ball.vY in speed_dependency:
            vY = speed_dependency[ball.vY]
        half_round = field_width / 2
        if (side.x < half_round and ball.x < half_round) or \
                (side.x > half_round and ball.x > half_round):
            val = side.y + side.height / 2
            if ball.y < val:
                pY = side.y - vY
            elif ball.y > val:
                pY =  side.y + vY
        if borders < pY < (field_height - side.height - borders):
            self.side.y = pY
            self.game.send_player_move(self)


    def on_game_exited(self):
        if self.ai_interval:
            ioloop.remove_timeout(self.ai_interval)

class AiHandler(object):

    def write_message(self, msg):
        pass

