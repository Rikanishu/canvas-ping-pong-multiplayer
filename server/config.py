
# Port for WS client connection
# Default is 8888
LISTEN_PORT = 8888

# Game server spawn workers count.
# Every worker will be wait two player before run game
WORKERS_SPAWN = 1

# Game type: "multiplayer" or "singleplayer" (with stupid ai)
GAME_TYPE = 'singleplayer'

# Server game loop FPS
# Number of game logic coordinates recalculating times per second
GAME_LOOP_FPS = 50

# Game field width in pixels
FIELD_WIDTH = 1024

# Game field height in pixels
FIELD_HEIGHT = 600

# Side padding for player in pixels
SIDE_PADDING = 20

# Top padding for player in pixels
TOP_PADDING = 20

# Player ping-pong racket size
SIDE_HEIGHT = 80
SIDE_WIDTH = 15

# Ball size and speed (min, max)
BALL_RADIUS = 10
BALL_MIN_SPEED = 6
BALL_MAX_SPEED = 12

# Number of AI logic recalculating times per second
AI_ACTIVE_LOOP = 35

