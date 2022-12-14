import turtle
import math
import random
from time import sleep
from copy import deepcopy
from enum import Enum
from typing import Union
from sys import argv
from timeit import default_timer as timer

VERTICES_COUNT = 6
SLEEP_TIME = 1.5

Line = tuple[int, int]


class Player(Enum):
    RED = 'red'
    BLUE = 'blue'

    def __invert__(self) -> 'Player':
        return Player.RED if self == Player.BLUE else Player.BLUE


class MinimaxType(Enum):
    MIN = 0
    MAX = 1

    def __invert__(self) -> 'MinimaxType':
        return MinimaxType.MIN if self == MinimaxType.MAX else MinimaxType.MAX


def winner(player_moves: dict[Player, list[Line]]) -> tuple[Union[Player, None], Union[tuple[Line, Line, Line], None]]:
    for color, moves in player_moves.items():
        if len(moves) < 3:
            continue
        for i in range(0, len(moves) - 2):
            for j in range(i + 1, len(moves) - 1):
                for k in range(j + 1, len(moves)):
                    if len(set(moves[i] + moves[j] + moves[k])) == 3:
                        return ~color, (moves[i], moves[j], moves[k])
    return None, None


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

    def _draw_line(self, p1: Dot, p2: Dot, color: str, pensize: int = 5) -> None:
        turtle.up()
        turtle.pensize(pensize)
        turtle.goto(p1)
        turtle.down()
        turtle.color(color)
        turtle.goto(p2)

    def _draw_board(self) -> None:
        for dot in self._dots:
            self._draw_dot(dot[0], dot[1], 'dark gray')

    def _lineToDots(self, line: Line) -> tuple[Dot, Dot]:
        return ((math.cos(math.radians(line[0] * 360 // self._vertices_count)),
                 math.sin(math.radians(line[0] * 360 // self._vertices_count))),
                (math.cos(math.radians(line[1] * 360 // self._vertices_count)),
                 math.sin(math.radians(line[1] * 360 // self._vertices_count))))

    def draw(self, player_moves: dict[Player, list[Line]] = {}) -> None:
        turtle.clear()
        self._draw_board()
        for color, moves in player_moves.items():
            for move in moves:
                self._draw_line(*self._lineToDots(move), color.value)
        self._screen.update()

    def show_triangle(self, triangle: tuple[Line, Line, Line]) -> None:
        for line in triangle:
            self._draw_line(*self._lineToDots(line), 'white', 3)
        self._screen.update()

    def close(self) -> None:
        self._screen.bye()


class MinimaxNode:
    _type: MinimaxType
    _value: float
    _children: list['MinimaxNode']
    _parent: Union['MinimaxNode', None]
    _move: Union[Line, None]
    _player: Player
    _depth: int
    _max_depth: int
    _prune: bool
    _alpha: float
    _beta: float
    _available_moves: list[Line]
    _player_moves: dict[Player, list[Line]]

    def __init__(self, parent: Union['MinimaxNode', None] = None, available_moves: list[Line] = [],
                 player_moves: dict[Player, list[Line]] = {}, prune: bool = False, max_depth: int = 1):
        self._parent = parent
        self._move = None
        self._children = []
        self._value = 0
        self._type = MinimaxType.MAX if not parent else ~parent._type
        self._depth = 0 if not parent else parent._depth + 1
        self._max_depth = parent._max_depth if parent else max_depth
        self._player = Player.RED if not parent else ~parent._player
        self._alpha = -math.inf if not parent else parent._alpha
        self._beta = math.inf if not parent else parent._beta
        self._available_moves = deepcopy(parent._available_moves) if parent else deepcopy(available_moves)
        self._player_moves = {player: deepcopy(moves) for player, moves in parent._player_moves.items()} if parent else \
            {player: deepcopy(moves) for player, moves in player_moves.items()}
        self._prune = parent._prune if parent else prune

    def _evaluate(self) -> float:
        w = winner(self._player_moves)[0]
        if w is not None:
            return math.inf if w == Player.RED else -math.inf
        h = 0
        for move in self._available_moves:
            res = winner({self._player: self._player_moves[self._player] + [move]})[0]
            if not res:
                h += 1
            elif res == self._player:
                h += 10
            else:
                h -= 8
        return h if self._player == Player.RED else -h

    def _minimax(self) -> float:
        if winner(self._player_moves)[0] is not None or self._depth == self._max_depth:
            self._value = self._evaluate()
            return self._value
        self._value = -math.inf if self._type == MinimaxType.MAX else math.inf
        for move in deepcopy(self._available_moves):
            self._available_moves.remove(move)
            self._player_moves[self._player].append(move)
            child = MinimaxNode(self)
            self._children.append(child)

            if self._type == MinimaxType.MAX:
                if child._minimax() >= self._value:
                    self._value = child._value
                    self._move = move
                if self._prune and self._value >= self._beta:
                    break
                self._alpha = max(self._alpha, self._value)
            else:
                if child._minimax() <= self._value:
                    self._value = child._value
                    self._move = move
                if self._prune and self._value <= self._alpha:
                    break
                self._beta = min(self._beta, self._value)

            self._player_moves[self._player].remove(move)
            self._available_moves.append(move)
        return self._value

    def get_best_move(self) -> Line:
        self._minimax()
        return self._move  # type: ignore


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

    def _initialize(self) -> None:
        self._available_moves = []
        for i in range(0, VERTICES_COUNT):
            for j in range(i, VERTICES_COUNT):
                if i != j:
                    self._available_moves.append((i, j))
        self._turn = random.choice([Player.RED, Player.BLUE])
        self._player_moves = {player: [] for player in Player}
        if self._gui:
            self._gui.draw()

    def _swap_turn(self) -> None:
        self._turn = ~self._turn

    def _minimax(self) -> tuple[Line, float]:
        root = MinimaxNode(available_moves=self._available_moves, player_moves=self._player_moves,
                           prune=self._prune, max_depth=self._minimax_depth)
        return root.get_best_move(), root._value

    def _enemy_move(self) -> Line:
        return random.choice(self._available_moves)

    def _game_over(self) -> tuple[Union[Player, None], Union[tuple[Line, Line, Line], None]]:
        return winner(self._player_moves)

    def play(self) -> Player:
        self._initialize()
        while True:
            selection = self._minimax()[0] if self._turn == Player.RED else self._enemy_move()
            selection = tuple(sorted(selection))

            if selection in self._player_moves.values():
                raise Exception("Duplicate Move!")

            self._player_moves[self._turn].append(selection)
            self._available_moves.remove(selection)
            self._swap_turn()
            if self._gui:
                self._gui.draw(self._player_moves)
                sleep(SLEEP_TIME)
            res = self._game_over()
            if res[0]:
                if self._gui:
                    self._gui.show_triangle(res[1]) # type: ignore
                    sleep(SLEEP_TIME)
                return res[0]

    def close(self) -> None:
        if self._gui:
            self._gui.close()


def calcWinChanceAndTime(depth: int, prune: bool, test_count: int) -> None:
    game = Sim(minimax_depth=depth, prune=prune, gui=False)
    start = timer()
    result = {p: 0 for p in Player}
    for _ in range(test_count):
        res = game.play()
        result[res] += 1
    end = timer()
    print(result)
    print(f"Depth: {depth}, Prune: {prune}")
    print(f"Time: {(end - start) / test_count:.4f}s")
    print(f"Win chance: {result[Player.RED] * 100 // test_count}%")
    print()

def main():
    # game = Sim(minimax_depth=int(argv[1]), prune=True, gui=bool(int(argv[2])))
    # res = game.play()
    # print("Winner: ", res)
    # game.close()
    # calcWinChanceAndTime(1, False, 100)
    # calcWinChanceAndTime(3, False, 100)
    # calcWinChanceAndTime(5, False, 10)
    # calcWinChanceAndTime(1, True, 100)
    # calcWinChanceAndTime(3, True, 100)
    # calcWinChanceAndTime(4, True, 100)
    calcWinChanceAndTime(5, True, 50)
    # calcWinChanceAndTime(7, True, 50)
    # calcWinChanceAndTime(15, True, 5)


if __name__ == "__main__":
    main()
