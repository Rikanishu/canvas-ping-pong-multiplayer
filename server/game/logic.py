# encoding: utf-8

from __future__ import absolute_import, division, with_statement
from game.figures import Rect, Circle, is_object_collision

import datetime
import config


class Hub(object):

    def __init__(self):
        self.players = []

    def add_player(self, player):
        self.players.append(player)
        player.num = len(self.players)

    def remove_player(self, num):
        del self.players[num]

    def get_player(self, num):
        return self.players[num]

    def is_full(self):
        return len(self.players) == 2

    def is_ready_to_play(self):
        return self.is_full()

    def broadcast(self, message):
        for p in self.players:
            # print p.handler
            # print message
            if p.handler is not None:
                p.handler.write_message(message)


class PlayersMessagesHandler(object):

    def __init__(self, game):
        self.game = game
        self.handlers = {
            'pM': self.on_player_move
        }

    def on_player_move(self, data, player):
        current_y = data
        field_height = self.game.settings['fieldHeight']
        top_padding = self.game.settings['topPadding']
        restriction = player.side.height / 2 + top_padding < current_y < \
                      field_height - player.side.height / 2 - top_padding
        if restriction:
            player.side.y = current_y - player.side.height / 2
        self.game.send_player_move(player)

    def handle(self, message, player):
        # print message
        try:
            if message[0]:
                if message[0] in self.handlers:
                    self.handlers[message[0]](message[1] or None, player)
        except Exception as e:
            print "Exception while handling player message: " + e.message


class Game(object):

    def __init__(self, hub, settings, ioloop):
        f_height = settings['fieldHeight']
        f_width = settings['fieldWidth']
        s_pad = settings['sidePadding']
        s_height = settings['sideHeight']
        s_width = settings['sideWidth']
        players_y = (f_height / 2) - (s_height / 2)
        hub.players[0].side = Rect(s_pad, players_y, s_width, s_height)
        hub.players[1].side = Rect((f_width - (s_width + s_pad)), players_y, s_width, s_height)
        b_radius = settings['ballRadius']
        self.hub = hub
        b_min_speed = settings['ballMinSpeed']
        self.ball = Circle(f_width / 2, f_height / 2, b_radius, 0, b_min_speed)
        self.settings = settings
        self.game_loop_interval = None
        self.started = False
        self.ioloop = ioloop
        self.msg_handler = PlayersMessagesHandler(self)
        self.scores = [0, 0]
        hub.players[0].enter_game(self)
        hub.players[1].enter_game(self)
        self.run_game()

    def run_game(self):
        self.send_init_state()
        self.started = True
        self.ioloop.add_timeout(datetime.timedelta(milliseconds=(500)), self.game_loop)

    def game_loop(self):
        self.update_ball()
        interval = self.ioloop.add_timeout(datetime.timedelta(milliseconds=(1000/config.GAME_LOOP_FPS)), self.game_loop)
        self.game_loop_interval = interval

    def update_ball(self):
        ball_max_speed = self.settings['ballMaxSpeed']
        field_height = self.settings['fieldHeight']
        field_width = self.settings['fieldWidth']
        ball = self.ball
        prev_vx = ball.vX
        prev_vy = ball.vY
        if ball.y < 0 or ball.y + ball.radius > field_height:
            ball.vY = -ball.vY
        if ball.x < 0:
            ball.vX = -ball.vX
            self.add_score(1)
        if ball.x + ball.radius > field_width:
            ball.vX = -ball.vX
            self.add_score(0)
        if (is_object_collision(self.hub.players[1].side, ball) and ball.vX > 0) or \
                (is_object_collision(self.hub.players[0].side, ball) and ball.vX < 0):
            if ball_max_speed > ball.vX > -ball_max_speed:
                if ball.vX < 0:
                    ball.vX -= 1
                else:
                    ball.vX += 1
                if ball.vY < 0:
                    ball.vY -= 1
                else:
                    ball.vY += 1
            ball.vX = -ball.vX
        ball.x += ball.vX
        ball.y += ball.vY
        if ball.vX != prev_vx or ball.vY != prev_vy:
            self.send_interactive_model()

    def send_interactive_model(self):
        model = {
            'b': {
                'x': self.ball.x,
                'y': self.ball.y,
                'vX': self.ball.vX,
                'vY': self.ball.vY
            }
        }
        self.hub.broadcast(['uIm', model])

    def send_player_move(self, player):
        state = []
        for p in self.hub.players:
            state.append(p.side.y)
        self.hub.broadcast(['uS', state])

    def send_init_state(self):
        state = {'p': []}
        for p in self.hub.players:
            state['p'].append({
                'x': p.side.x,
                'y': p.side.y,
                'h': p.side.height,
                'w': p.side.width,
            })
        state['b'] = {
            'x': self.ball.x,
            'y': self.ball.y,
            'r': self.ball.radius,
            'vX': self.ball.vX,
            'vY': self.ball.vY
        }
        state['f'] = {
            'h': self.settings['fieldHeight'],
            'w': self.settings['fieldWidth']
        }
        #for player in self.hub.players:
        #    state['n'] = player.num
        #    player.handler.write_message(state)
        self.hub.broadcast(['iS', state])

    def add_score(self, player_num):
        self.scores[player_num] += 1
        self.hub.broadcast(['uSc', self.scores])

    def finish_game(self):
        if self.game_loop_interval:
            self.ioloop.remove_timeout(self.game_loop_interval)
        for p in self.hub.players:
            p.exit_game()

    def on_player_message(self, message, player):
        self.msg_handler.handle(message, player)

    def on_player_exit(self, player):
        self.hub.remove_player(player.num)
        self.finish_game()


class Player(object):

    def __init__(self, handler):
        self.handler = handler
        self.game = None
        self.in_game = False

    def enter_game(self, game):
        self.game = game
        self.in_game = True
        self.on_game_connected()

    def exit_game(self):
        self.game = None
        self.in_game = True
        self.on_game_exited()

    def on_game_connected(self):
        pass

    def on_game_exited(self):
        pass