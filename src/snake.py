import pyglet
from pyglet.window import key

from game import Arena, Direction

width = 1000
height = 800

# initialize Snake game arena
arena = Arena(height, width, speed=1.0 / 20)

window = pyglet.window.Window(width, height)


@window.event
def on_key_press(symbol, _):
    keymap = {key.UP: Direction.UP,
              key.DOWN: Direction.DOWN,
              key.LEFT: Direction.LEFT,
              key.RIGHT: Direction.RIGHT}
    if symbol in keymap:
        arena.snake.change_direction(keymap[symbol])
    if symbol == key.SPACE:
        arena.restart_game()


@window.event
def on_draw():
    window.clear()
    arena.draw()


def main():
    pyglet.clock.schedule_interval(arena.update, 1.0 / 100)
    pyglet.app.run()


if __name__ == '__main__':
    main()
