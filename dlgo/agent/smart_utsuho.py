"""
    程序最重要的是完成select_move函数
    该函数读入一个状态 并根据状态返回一个认为最佳的move
"""

import random
from dlgo.agent.base import Agent
from dlgo.goboard_slow import Move
from dlgo.gotypes import Point
from dlgo.scoring import evaluate_win
from dlgo.scoring import evaluate_link
from dlgo.gotypes import Player


class Smart_Utsuho(Agent):
    def __init__(self, layer_limit):
        super().__init__()
        self.layer_limit = layer_limit

    #  阿空的完美五子棋教室
    def select_move(self, game_state):
        candidates = self.find_candidate_action(game_state)
        # 若不存在一个合法的落子点 即候选数组为空
        if not candidates:
            # 返回pass
            return Move.pass_turn(), None

        action, estimation = self.thinking_action(game_state, game_state.next_player, None, 1)
        return action, estimation

    @classmethod
    def find_candidate_action(cls, game_state):
        if game_state.previous_state is None:
            return [Point(7, 7)]

        # 候选者落子点数组
        candidates = []
        # 遍历棋盘的每一个点 找到所有合法落子点
        for r in range(1, game_state.board.num_rows + 1):
            for c in range(1, game_state.board.num_cols + 1):
                # 该点的point数据结构
                candidate = Point(row=r, col=c)
                # 判断该落子点对于该阵营是否合法
                if game_state.is_valid_move(Move.play(candidate)):
                    if is_there_adjacent(candidate, game_state.board):
                        # 若合法 则加入到数组中
                        candidates.append(candidate)
        return candidates

    @classmethod
    def action_consequence(cls, game_state, move):
        return game_state.apply_move(move)

    def thinking_action(self, game_state, faction, mother_estimation, layer):
        now_estimation = None

        candidates = self.find_candidate_action(game_state)

        win_actions = []
        tie_actions = []
        tie_estimations = []
        lose_actions = []

        for point in candidates:

            move = Move.play(point)
            new_state = self.action_consequence(game_state, move)
            winner = evaluate_win(new_state.board, move)

            winner_estimation = 0

            # 未完成的情况
            if winner is None:
                if layer <= self.layer_limit:
                    action, winner_estimation = \
                        self.thinking_action(new_state, change_faction(faction), now_estimation, layer + 1)
                else:
                    estimated_value = heuristic_estimation(new_state)
                    action, winner_estimation = move, estimated_value

                """
                    α-β剪枝
                """
                if now_estimation is None:
                    now_estimation = winner_estimation
                else:
                    if judge_estimation_better(now_estimation, winner_estimation, faction):
                        now_estimation = winner_estimation

                if mother_estimation is not None:
                    # 母亲节点是否比本节点更【好】（对母亲节点而言的好）
                    # 如果不比母亲节点更好 相等乃至更烂 则不再继续
                    if not judge_estimation_better(mother_estimation, now_estimation, change_faction(faction)):
                        if faction == Player.black:
                            return move, 10000
                        else:
                            return move, -10000
                """
                    α-β剪枝
                """
                if isinstance(winner_estimation, (int, float)):
                    tie_actions.append(move)
                    tie_estimations.append(winner_estimation)

                elif winner_estimation == faction:
                    print("warning: there is a bug here. code:008")
                    # return move, 10000
                elif winner_estimation == change_faction(faction):
                    print("warning: there is a bug here. code:009")
                    # lose_actions.append(move)
                elif winner_estimation is None:
                    print("warning: there is a bug here. code:001")
                else:
                    print("warning: there is a bug here. code:003")

            # 胜负的情况
            else:
                if winner == faction:
                    if faction == Player.black:
                        return move, 10000
                    else:
                        return move, -10000
                elif winner == change_faction(faction):
                    lose_actions.append(move)
                else:
                    print("warning: there is a bug here. code:002")

        if tie_actions:
            if faction == Player.black:
                good_value = max(tie_estimations)
            else:
                good_value = min(tie_estimations)
            best_estimated_action = tie_actions[tie_estimations.index(good_value)]
            return best_estimated_action, good_value
        elif lose_actions:
            if faction == Player.black:
                return random.choice(lose_actions), -10000
            else:
                return random.choice(lose_actions), 10000
        elif win_actions:
            print("warning: there is a bug here. code:010")
            # return random.choice(win_actions), 10000
        else:
            print("warning: there is a bug here. code:006")


def change_faction(faction):
    if faction == Player.white:
        return Player.black
    elif faction == Player.black:
        return Player.white


# winner_estimation 是否比 now_estimation 好
def judge_estimation_better(now_estimation, winner_estimation, faction):
    if now_estimation is None:
        return False

    # def get_mark(now_faction_estimation, self_faction):
    #     if isinstance(now_faction_estimation, (int, float)):
    #         return now_faction_estimation
    #     elif now_faction_estimation == self_faction:
    #         print("warning: there is a bug here. code:011")
    #         # return 10000
    #     elif now_faction_estimation == change_faction(self_faction):
    #         print("warning: there is a bug here. code:012")
    #         # return -10000
    #     elif now_faction_estimation is False:
    #         print("warning: there is a bug here. code:007")
    #     else:
    #         print("warning: there is a bug here. code:005")

    # now_mark = get_mark(now_estimation, faction)
    # new_mark = get_mark(winner_estimation, faction)

    if faction == Player.black:
        return winner_estimation > now_estimation
    else:
        return winner_estimation < now_estimation


def heuristic_estimation(game_state):
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    # 黑分和白分
    value = 0

    for stone_positions_point in game_state.board.get_stones_positions_points():
        for direction in directions:
            link_long = evaluate_open_link(game_state.board, stone_positions_point, direction)
            if link_long >= 1:
                if game_state.board.get(stone_positions_point) == Player.black:
                    value += link_long ** 3
                else:
                    value -= link_long ** 3

    # 黑队有利性
    return value


def is_there_adjacent(point, board):
    if len(board.get_stones_positions_points()) == 0:
        return True

    for r in range(point.row - 2, point.row + 3):
        if board.num_rows >= r >= 1:
            for c in range(point.col - 2, point.col + 3):
                if board.num_cols >= c >= 1:
                    if point.row != r or point.col != c:
                        if board.get(Point(row=r, col=c)):
                            return True

    return False


def evaluate_open_link(board, stone_position_point, direction, vert=False):
    link_num = 1
    gate = False

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
    else:
        if board.get(now_position_point) == change_faction(original_stone) or \
                board.num_rows <= now_position_point.row <= 1 or \
                board.num_cols <= now_position_point.col <= 1:
            gate = True

    # 反方向延伸
    degree = 1
    now_position_point = Point(row=stone_position_point.row - direction[0],
                               col=stone_position_point.col - direction[1])
    while board.get(now_position_point) == original_stone:
        now_position_point = Point(row=now_position_point.row - direction[0],
                                   col=now_position_point.col - direction[1])
        link_num += 1
        degree += 1
    else:
        if board.get(now_position_point) == change_faction(original_stone) or \
                board.num_rows <= now_position_point.row <= 1 or \
                board.num_cols <= now_position_point.col <= 1:
            if gate:
                link_num = 1
            else:
                link_num -= 1.5

    return link_num
