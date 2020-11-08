import random
from collections import namedtuple
from enum import Enum

import numpy as np
import pyglet
from pyglet.window import key
from pyglet import shapes

width = 1000
height = 800

window = pyglet.window.Window(width, height)

label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width // 2, y=window.height // 2,
                          anchor_x='center', anchor_y='center')


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class BoardEntity(Enum):
    BORDER = 1
    NOTHING = 2
    APPLE = 3


Dimensions = namedtuple('Dimensions', ['rows', 'cols'])


class SnakePart:
    def __init__(self, x: int, y: int, direction: Direction):
        self.location = (x, y)
        self.direction = direction


class Snake:
    def __init__(self, dimensions: Dimensions, x: int, y: int):
        self.dimensions = dimensions
        self.border_size = 1
        self.head = SnakePart(x, y, Direction.UP)
        self.body = []

    def change_direction(self, direction: Direction):
        self.head.direction = direction

    def update_pos(self, pos: SnakePart, next_direction: Direction) -> SnakePart:
        x, y = pos.location
        new_pos = {
            Direction.UP: (x, y + 1),
            Direction.DOWN: (x, y - 1),
            Direction.LEFT: (x - 1, y),
            Direction.RIGHT: (x + 1, y)
        }[pos.direction]

        # handle sides, infinite run
        col_max = self.dimensions.cols - 1 - self.border_size
        row_max = self.dimensions.rows - 1 - self.border_size

        if col_max - new_pos[0] < 0:
            new_pos = (self.border_size, new_pos[1])

        if new_pos[0] - self.border_size < 0:
            new_pos = (col_max, new_pos[1])

        if row_max - new_pos[1] < 0:
            new_pos = (new_pos[0], self.border_size)

        if new_pos[1] - self.border_size < 0:
            new_pos = (new_pos[0], row_max)

        pos.location = new_pos
        pos.direction = next_direction

        return pos

    def update(self, eat_apple: bool):
        if eat_apple:
            self.body.append(SnakePart(self.head.location[0], self.head.location[1], self.head.direction))
        else:
            size = len(self.body)
            for i in range(size):
                current = self.body[i]
                if i == size - 1:
                    next = self.head
                else:
                    next = self.body[i + 1]

                self.update_pos(current, next.direction)

        self.update_pos(self.head, self.head.direction)


class Arena:
    def __init__(self):
        self.grid_size = 40
        self.step_size = 1.0 / 10
        self.dimensions = Dimensions(rows=height // self.grid_size, cols=width // self.grid_size)

        self.game = np.empty([self.dimensions.rows, self.dimensions.cols], dtype=BoardEntity)
        self.last_run = 0
        self.timestamp = 0

        self.generate_game()
        self.snake = self.generate_snake()
        self.spawn_apple()

    def generate_game(self):
        for row in range(self.dimensions.rows):
            for col in range(self.dimensions.cols):
                if col == 0 or row == 0 or col == self.dimensions.cols - 1 or row == self.dimensions.rows - 1:
                    self.game[row][col] = BoardEntity.BORDER
                else:
                    self.game[row][col] = BoardEntity.NOTHING

    def new_snake(self):
        self.snake = self.generate_snake()

    def generate_snake(self) -> Snake:
        random_row = random.randrange(1, self.dimensions.rows - 1)
        random_col = random.randrange(1, self.dimensions.cols - 1)
        return Snake(self.dimensions, random_col, random_row)

    def spawn_apple(self):
        random_row = random.randrange(1, self.dimensions.rows - 1)
        random_col = random.randrange(1, self.dimensions.cols - 1)
        self.game[random_row][random_col] = BoardEntity.APPLE

    def update(self, dt: float):
        self.timestamp += dt
        if self.timestamp - self.last_run < self.step_size:
            return
        self.last_run = self.timestamp

        eat_apple = self.is_apple(self.snake.head.location)
        if eat_apple:
            x, y = self.snake.head.location
            self.game[y][x] = BoardEntity.NOTHING
            self.spawn_apple()
        self.snake.update(eat_apple)

    def is_apple(self, loc) -> bool:
        return self.game[loc[1]][loc[0]] == BoardEntity.APPLE

    def draw(self):
        batch = pyglet.graphics.Batch()
        s = []

        for row in range(self.dimensions.rows):
            for col in range(self.dimensions.cols):
                x = col * self.grid_size
                y = row * self.grid_size
                board_entity = self.game[row][col]
                if board_entity == BoardEntity.BORDER:
                    s.append(shapes.Rectangle(x, y, self.grid_size, self.grid_size,
                                              color=(230,
                                                     170,
                                                     40), batch=batch))
                elif board_entity == BoardEntity.APPLE:
                    s.append(shapes.Rectangle(x, y, self.grid_size, self.grid_size,
                                              color=(0,
                                                     210,
                                                     0), batch=batch))
                else:
                    s.append(shapes.Rectangle(x, y, self.grid_size, self.grid_size,
                                              color=(20, 20, 20), batch=batch))

        snake = self.snake

        for body_part in snake.body:
            body_part_location = body_part.location
            s.append(shapes.Rectangle(body_part_location[0] * self.grid_size, body_part_location[1] * self.grid_size,
                                      self.grid_size,
                                      self.grid_size,
                                      color=(100, 0, 0), batch=batch))

        head_loc = self.snake.head.location
        s.append(shapes.Rectangle(head_loc[0] * self.grid_size, head_loc[1] * self.grid_size, self.grid_size,
                                  self.grid_size,
                                  color=(200, 0, 0), batch=batch))

        batch.draw()


arena = Arena()


@window.event
def on_key_press(symbol, _):
    keymap = {key.UP: Direction.UP,
              key.DOWN: Direction.DOWN,
              key.LEFT: Direction.LEFT,
              key.RIGHT: Direction.RIGHT}
    if symbol in keymap:
        arena.snake.change_direction(keymap[symbol])
    if symbol == key.SPACE:
        arena.new_snake()


@window.event
def on_draw():
    window.clear()
    arena.draw()


def main():
    pyglet.clock.schedule_interval(arena.update, 1.0 / 100)
    pyglet.app.run()


if __name__ == '__main__':
    main()
