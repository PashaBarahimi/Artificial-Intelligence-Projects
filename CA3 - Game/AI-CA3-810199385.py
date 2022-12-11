from select import select
import turtle
import math
import random
from time import sleep
from enum import Enum
from dataclasses import dataclass
from typing import Union
from sys import argv


class Player(Enum):
    RED = 'red'
    BLUE = 'blue'

    def __invert__(self) -> 'Player':
        return Player.RED if self == Player.BLUE else Player.BLUE


@dataclass
class Sim:
    _gui: bool
    _screen: Union[turtle._Screen, None]
    _selection: list
    _turn: Player
    _dots: list
    _player_moves: dict
    _available_moves: list
    _minimax_depth: int
    _prune: bool

    def __init__(self, minimax_depth, prune, gui):
        self._gui = gui
        self._prune = prune
        self._minimax_depth = minimax_depth
        if self._gui:
            self._setup_screen()
        else:
            self._screen = None
        self._player_moves = {
            Player.RED: [],
            Player.BLUE: []
        }
        self._initialize()

    def _setup_screen(self) -> None:
        self._screen = turtle.Screen()
        self._screen.setup(800, 800)
        self._screen.title("Game of SIM")
        self._screen.setworldcoordinates(-1.5, -1.5, 1.5, 1.5)
        self._screen.tracer(0, 0)
        turtle.hideturtle()

    def _draw_dot(self, x: float, y: float, color: str) -> None:
        turtle.up()
        turtle.goto(x, y)
        turtle.color(color)
        turtle.dot(15)

    def _gen_dots(self) -> list[tuple[float, float]]:
        r = []
        for angle in range(0, 360, 60):
            r.append((math.cos(math.radians(angle)),
                     math.sin(math.radians(angle))))
        return r

    def _initialize(self) -> None:
        self._selection = []
        self._available_moves = []
        for i in range(0, 6):
            for j in range(i, 6):
                if i != j:
                    self._available_moves.append((i, j))
        self._turn = Player.RED if random.randint(0, 2) == 1 else Player.BLUE
        self._dots = self._gen_dots()
        if self._gui:
            turtle.clear()
        self._draw()

    def _draw_line(self, p1: tuple[float, float], p2: tuple[float, float], color: str) -> None:
        turtle.up()
        turtle.pensize(3)
        turtle.goto(p1)
        turtle.down()
        turtle.color(color)
        turtle.goto(p2)

    def _draw_board(self) -> None:
        for i in range(len(self._dots)):
            if i in self._selection:
                self._draw_dot(self._dots[i][0], self._dots[i][1], self._turn.value)
            else:
                self._draw_dot(self._dots[i][0], self._dots[i][1], 'dark gray')

    def _draw(self) -> None:
        if not self._gui:
            return
        self._draw_board()
        for color, moves in self._player_moves.items():
            for move in moves:
                self._draw_line((math.cos(math.radians(move[0] * 60)), math.sin(math.radians(move[0] * 60))),
                                (math.cos(math.radians(move[1] * 60)), math.sin(math.radians(move[1] * 60))),
                                color.value)
        if self._screen is not None:
            self._screen.update()
        sleep(1)

    def _evaluate(self):
        # TODO
        pass

    def _swap_turn(self) -> None:
        self._turn = ~self._turn

    def _minimax(self):
        # TODO
        pass

    def _enemy(self) -> tuple[int, int]:
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
        while True:
            if self._turn == Player.RED:
                selection = self._minimax()[0]
                if selection[1] < selection[0]:
                    selection = (selection[1], selection[0])
            else:
                selection = self._enemy()
                if selection[1] < selection[0]:
                    selection = (selection[1], selection[0])
            if selection in self._player_moves[Player.RED] or selection in self._player_moves[Player.BLUE]:
                raise Exception("Duplicate Move!!!")
            self._player_moves[self._turn].append(selection)

            self._available_moves.remove(selection)
            selection = []
            self._draw()
            res = self._gameover()
            if res:
                return res


def main():
    game = Sim(minimax_depth=int(argv[1]), prune=True, gui=bool(int(argv[2])))

    results = {
        Player.RED: 0,
        Player.BLUE: 0
    }
    for i in range(10):
        print(f"Game {i}")
        results[game.play()] += 1

    print(results)


if __name__ == "__main__":
    main()
