# tag::scoring_imports[]
from __future__ import absolute_import
from collections import namedtuple

from dlgo.gotypes import Player, Point
# end::scoring_imports[]


# tag::scoring_game_result[]
class GameResult(namedtuple('GameResult', 'winner')):
    @property
    def get_winner(self):
        return self.winner

    def __str__(self):
        name = ""
        if self.winner == Player.black:
            name = "black"
        elif self.winner == Player.white:
            name = "white"
        else:
            name = "nobody"
        return name + " is winner"
# end::scoring_game_result[]


""" evaluate_territory:
Map a board into territory and dame.

Any points that are completely surrounded by a single color are
counted as territory; it makes no attempt to identify even
trivially dead groups.
"""


#
# tag::scoring_evaluate_territory[]
# 计算胜负
def evaluate_win(board, last_move):

    if last_move.point is None:
        return None

    winner = evaluate_goku(board, last_move.point)
    if winner:
        return winner

    return None


def evaluate_goku(board, stone_position_point):
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    for direction in directions:
        link_num = evaluate_link(board, stone_position_point, direction)
        if link_num >= 5:
            return board.get(stone_position_point)


def evaluate_link(board, stone_position_point, direction, vert=False):
    link_num = 1

    # 正方向延伸
    degree = 1
    now_position_point = Point(row=stone_position_point.row + direction[0],
                               col=stone_position_point.col + direction[1])

    if not vert:
        original_stone = board.get(stone_position_point)
    else:
        original_stone = change_faction(board.get(stone_position_point))

    while board.get(now_position_point) == original_stone:
        now_position_point = Point(row=now_position_point.row + direction[0],
                                   col=now_position_point.col + direction[1])
        link_num += 1
        degree += 1

    # 反方向延伸
    degree = 1
    now_position_point = Point(row=stone_position_point.row - direction[0],
                               col=stone_position_point.col - direction[1])
    while board.get(now_position_point) == original_stone:
        now_position_point = Point(row=now_position_point.row - direction[0],
                                   col=now_position_point.col - direction[1])
        link_num += 1
        degree += 1

    return link_num


# 计算赢家
# tag::scoring_compute_game_result[]
def compute_game_result(game_state):
    # 判断有没有连星
    winner = evaluate_win(game_state.board, game_state.last_move)
    return GameResult(winner)
# end::scoring_compute_game_result[]


def change_faction(faction):
    if faction == Player.white:
        return Player.black
    elif faction == Player.black:
        return Player.white
