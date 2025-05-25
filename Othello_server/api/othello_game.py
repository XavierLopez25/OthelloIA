from typing import Tuple
from datetime import datetime, timedelta

class OthelloGame():

    def __init__(self, game_id : str, white_player : str, black_player : str):
        self.gameid = game_id
        self.white_player = white_player
        self.black_player = black_player
        self.board = [[0] * 8 for _ in range(8)]
        self.board[3][3] = 1
        self.board[3][4] = -1
        self.board[4][3] = -1
        self.board[4][4] = 1

        self.current_player = -1
        self.score = {1: 2, -1 : 2}
        self.empty_squares = 60
        self.winner = None
        self.last_turn = None
        self.game_over = False
        self.strikes = {1 : 0, -1 : 0}
        self.last_move = {1 : 0 , -1 : 0}

    def display_board(self):
        for row in self.board:
            print('|'.join(map(str, row)))
            print('-' * 15)

    def update_board(self, player, row, col) -> (bool, str):

        if self.last_turn is None:
            self.last_turn = datetime.now()

        else:
            move_time = datetime.now()
            time_diff = move_time - self.last_turn

            valid_timeframe = time_diff < timedelta(seconds = 180)

            if not valid_timeframe:
                self.winner = -self.current_player
                self.game_over = True
                return False, 'OVERTIME'


        if self.is_valid_move(player, row, col):
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),(-1, -1), (-1, 1), (1, -1), (1, 1)]
            self.board[row][col] = self.current_player
            opponent = -self.current_player

            for direction in directions:
                pieces_to_flip = []
                dr, dc = direction
                r, c = row + dr, col + dc

                while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                    pieces_to_flip.append((r, c))
                    r += dr
                    c += dc

                if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == player:
                    for (fr, fc) in pieces_to_flip:
                        self.board[fr][fc] = player


            self.score[self.current_player] = 0
            self.score[opponent] = 0

            for i in range(8):
                for j in range(8):
                    if self.board[i][j] == self.current_player:
                        self.score[self.current_player] += 1
                    if self.board[i][j] == opponent:
                        self.score[opponent] += 1

            _game_over, _game_over_msg = self.check_game_over()

            self.last_turn = datetime.now()
            self.game_over = _game_over

            return True, 'VALID'

        else:
            return False, 'INVALID'

    def is_valid_move(self, player, row, col):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),(-1, -1), (-1, 1), (1, -1), (1, 1)]

        if self.board[row][col] != 0:
            return False

        opponent = -player

        for direction in directions:
            dr, dc = direction
            r, c = row + dr, col + dc
            found_opponent = False

            while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                r += dr
                c += dc
                found_opponent = True

            if found_opponent and 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == player:
                return True

        return False

    def valid_moves(self, player):
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(player, row, col):
                    valid_moves.append((row, col))

        return valid_moves

    def check_game_over(self) -> tuple[bool, str]:

        if self.strikes[1] >= 3:
            self.winner = self.black_player
            return True, 'Game Over'

        if self.strikes[-1] >= 3:
            self.winner = self.white_player
            return True, 'Game Over'

        # Check for valid moves for both players
        moves_opponent = self.valid_moves(-self.current_player)
        moves_current_player = self.valid_moves(self.current_player)

        if not moves_opponent and not moves_current_player:
            if self.score[1] > self.score[-1]:
                self.winner = self.white_player
            if self.score[-1] > self.score[1]:
                self.winner = self.black_player
            if self.score[-1] == self.score[1]:
                self.winner = 'Tie'
            return True, 'Game Over'
        else:
            if not moves_opponent:
                return False, 'Moves left'
            else:
                self.current_player = -self.current_player
                return False, 'Moves left'

    def strike(self):
        self.strikes[self.current_player] += 1

    def get_board(self):
        return self.board

if __name__ == '__main__':
    game = OthelloGame('test_game')
    game.display_board()
    game.update_board(game.current_player, 5,5)
    print('Move 1')
    game.display_board()



