import turtle
import math
import random
from time import sleep
from enum import Enum
from dataclasses import dataclass
from typing import Union
from sys import argv

VERTICES_COUNT = 6
SLEEP_TIME = 0.5

Line = tuple[int, int]


class Player(Enum):
    RED = 'red'
    BLUE = 'blue'

    def __invert__(self) -> 'Player':
        return Player.RED if self == Player.BLUE else Player.BLUE


class SimGui:
    Dot = tuple[float, float]

    def __init__(self, title: str, width: int, height: int, vertices_count: int):
        self._screen = turtle.Screen()
        self._screen.setup(width, height)
        self._screen.title(title)
        self._screen.setworldcoordinates(-1.5, -1.5, 1.5, 1.5)
        self._screen.tracer(0, 0)
        turtle.hideturtle()
        self._vertices_count = vertices_count
        self._gen_dots()
        self._draw_board()


    def _gen_dots(self) -> None:
        self._dots = []
        for angle in range(0, 360, 360 // self._vertices_count):
            self._dots.append((math.cos(math.radians(angle)),
                               math.sin(math.radians(angle))))

    def _draw_dot(self, x: float, y: float, color: str) -> None:
        turtle.up()
        turtle.goto(x, y)
        turtle.color(color)
        turtle.dot(15)

    def _draw_line(self, p1: Dot, p2: Dot, color: str) -> None:
        turtle.up()
        turtle.pensize(3)
        turtle.goto(p1)
        turtle.down()
        turtle.color(color)
        turtle.goto(p2)

    def _draw_board(self) -> None:
        for dot in self._dots:
            self._draw_dot(dot[0], dot[1], 'dark gray')

    def draw(self, player_moves: dict[Player, list[Line]] = {}) -> None:
        turtle.clear()
        self._draw_board()
        for color, moves in player_moves.items():
            for move in moves:
                self._draw_line((math.cos(math.radians(move[0] * 360 // self._vertices_count)),
                                 math.sin(math.radians(move[0] * 360 // self._vertices_count))),
                                (math.cos(math.radians(move[1] * 360 // self._vertices_count)),
                                 math.sin(math.radians(move[1] * 360 // self._vertices_count))),
                                color.value)
        self._screen.update()


@dataclass
class Sim:
    _gui: Union[SimGui, None]
    _turn: Player
    _player_moves: dict[Player, list[Line]]
    _available_moves: list[Line]
    _minimax_depth: int
    _prune: bool

    def __init__(self, minimax_depth: int, prune: bool, gui: bool):
        self._prune = prune
        self._minimax_depth = minimax_depth
        self._gui = SimGui('Game of Sim', 800, 800, VERTICES_COUNT) if gui else None
        self._player_moves = {player: [] for player in Player}

    def _initialize(self) -> None:
        self._available_moves = []
        for i in range(0, VERTICES_COUNT):
            for j in range(i, VERTICES_COUNT):
                if i != j:
                    self._available_moves.append((i, j))
        self._turn = random.choice([Player.RED, Player.BLUE])
        if self._gui:
            self._gui.draw()

    def _evaluate(self):
        # TODO
        pass

    def _swap_turn(self) -> None:
        self._turn = ~self._turn

    def _minimax(self):
        # TODO
        pass

    def _enemy_move(self) -> Line:
        return random.choice(self._available_moves)

    def _gameover(self) -> Union[Player, None]:
        for color, moves in self._player_moves.items():
            if len(moves) < 3:
                continue
            for i in range(len(moves) - 2):
                for j in range(i + 1, len(moves) - 1):
                    for k in range(j + 1, len(moves)):
                        if moves[i][0] == moves[j][0] and moves[i][1] == moves[k][0] and moves[j][1] == moves[k][1]:
                            return ~color
        return None

    def play(self) -> Player:
        self._initialize()
        while True:
            selection = self._minimax()[0] if self._turn == Player.RED else self._enemy_move()
            if selection[1] < selection[0]:
                selection = (selection[1], selection[0])

            if selection in self._player_moves.values():
                raise Exception("Duplicate Move!")

            self._player_moves[self._turn].append(selection)
            self._available_moves.remove(selection)
            self._swap_turn()
            if self._gui:
                self._gui.draw(self._player_moves)
                sleep(SLEEP_TIME)
            res = self._gameover()
            if res:
                return res


def main():
    game = Sim(minimax_depth=int(argv[1]), prune=True, gui=bool(int(argv[2])))

    results = {p: 0 for p in Player}
    for i in range(10):
        print(f"Game {i}:")
        results[game.play()] += 1

    print(results)


if __name__ == "__main__":
    main()
