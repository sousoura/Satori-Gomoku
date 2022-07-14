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


class Smart_Sanyousei(Agent):
    def __init__(self, layer_limit):
        super().__init__()
        self.layer_limit = layer_limit

    #  三月精的完美五子棋教室
    def select_move(self, game_state):
        candidates = self.find_candidate_action(game_state)
        # 若不存在一个合法的落子点 即候选数组为空
        if not candidates:
            # 返回pass
            return Move.pass_turn(), None

        action, estimation = self.thinking_action(game_state, game_state.next_player, None, 1)
        # print("sanyousei:", estimation)
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

    if faction == Player.black:
        return winner_estimation > now_estimation
    else:
        return winner_estimation < now_estimation


def heuristic_estimation(game_state):
    final_value = 0
    game_shapes = [
        # 连五
        "11111",
        # 活四
        "011110",
        # 冲四
        "211110", "011112", "10111", "11011", "11101",
        # 活三
        "0011100", "011010", "010110", "2011100", "0011102",
        # 眠三
        "211100", "2110100", "2101100", "001112", "0011012", "0010112", "0100110", "0101010", "2011102",
        # 活二
        "001100", "01010", "010010",
        # 眠二
        "211000", "210010", "10001", "210100", "2010102", "2001102", "2011002", "2100012"
    ]

    game_shape_names = [
        # 连五
        "连五",
        # 活四
        "活四",
        # 冲四
        "冲四", "冲四", "冲四", "冲四", "冲四",
        # 活三
        "活三", "活三", "活三", "活三", "活三",
        # 眠三
        "眠三", "眠三", "眠三", "眠三", "眠三", "眠三", "眠三", "眠三", "眠三",
        # 活二
        "活二", "活二", "活二",
        # 眠二
        "眠二", "眠二", "眠二", "眠二", "眠二", "眠二", "眠二", "眠二"
    ]

    rewards = [
        100000,
        50000,
        5000, 5000, 5000, 5000, 5000,
        1000, 1000, 1000, 1000, 1000,
        500, 500, 500, 500, 500, 500, 500, 500, 500,
        100, 100, 100,
        20, 20, 20, 20, 20, 20, 20, 20
    ]

    black_list_board = game_state.board.get_list_board(rev=False)
    white_list_board = game_state.board.get_list_board(rev=True)

    def cal_mark(list_board):
        value = 0

        def find_game_shape(line):
            string_line = "2" + ''.join(line) + "2"
            # print(string_line)
            mark = 0
            for shape_index in range(len(game_shapes)):
                if game_shapes[shape_index] in string_line:
                    mark += rewards[shape_index]
                    # 测试
                    # print("shape", game_shape_names[shape_index])
            return mark

        # print("横向")
        for row in list_board:
            if "1" in row:
                value += find_game_shape(row)

        # print("纵向")
        for col_index in range(len(list_board)):
            col = [i[col_index] for i in list_board]
            if "1" in col:
                value += find_game_shape(col)

        # print("斜向")
        for oblique_index in range(1, len(list_board)):
            left_falling = ""
            right_falling = ""

            for ind in range(oblique_index + 1):
                left_falling += list_board[len(list_board) - 1 - oblique_index + ind][len(list_board) - 1 - ind]
                right_falling += list_board[len(list_board) - 1 - oblique_index + ind][ind]

            if "1" in left_falling:
                # print("撇")
                # print(left_falling)
                value += find_game_shape(left_falling)

            if "1" in right_falling:
                # print("捺")
                # print(right_falling)
                value += find_game_shape(right_falling)

        # print("斜向")
        for oblique_index in range(len(list_board) - 1, 0, -1):
            left_falling = ""
            right_falling = ""

            for ind in range(oblique_index + 1):
                left_falling += list_board[ind][oblique_index - ind]
                right_falling += list_board[ind][len(list_board) - 1 - oblique_index + ind]

            if "1" in left_falling:
                # print("撇")
                # print(left_falling)
                value += find_game_shape(left_falling)

            if "1" in right_falling:
                # print("捺")
                # print(right_falling)
                value += find_game_shape(right_falling)

        return value

    # print("白")
    # for line in white_list_board:
    #     print(line)
    final_value -= cal_mark(white_list_board)
    # print("黑")
    # for line in black_list_board:
    #     print(line)
    final_value += cal_mark(black_list_board)

    board_mid = game_state.board.num_cols // 2
    for point in game_state.board.get_stones_positions_points():
        if game_state.board.get(point) == Player.black:
            final_value += ((point.row - board_mid) ** 2 + (point.col - board_mid) ** 2) ** 0.5
        else:
            final_value -= ((point.row - board_mid) ** 2 + (point.col - board_mid) ** 2) ** 0.5

    return final_value


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
