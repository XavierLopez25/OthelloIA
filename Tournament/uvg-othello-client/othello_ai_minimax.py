import random
import math
import time
from minimax_ai import minimax

DIRECTIONS = [
    (-1, -1),  # UP-LEFT
    (-1, 0),   # UP
    (-1, 1),   # UP-RIGHT
    (0, -1),   # LEFT
    (0, 1),    # RIGHT
    (1, -1),   # DOWN-LEFT
    (1, 0),    # DOWN
    (1, 1)     # DOWN-RIGHT
]

def in_bounds(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def valid_movements(board, player):
    opponent = -player
    valid_moves = []

    for x in range(8):
        for y in range(8):
            if board[x][y] != 0:
                continue

            for dx, dy in DIRECTIONS:
                i, j = x + dx, y + dy
                found_opponent = False

                while in_bounds(i, j) and board[i][j] == opponent:
                    i += dx
                    j += dy
                    found_opponent = True

                if found_opponent and in_bounds(i, j) and board[i][j] == player:
                    valid_moves.append((x, y))
                    break

    return valid_moves
 
def ai_move(board, player, time_limit=3):
    """
    board: matriz 8x8
    player: 1 (white) o -1 (black)
    """
    start = time.time()
    best_move = None
    depth = 1
    opponent = -player

    # iterative deepening hasta agotar time_limit
    while True:
        try:
            _, mv = minimax(
                board, player, depth,
                -math.inf, math.inf,
                True, opponent,
                start, time_limit, True
            )
            if mv is not None:
                best_move = mv
            depth += 1
        except TimeoutError:
            break

    # fallback: elige legal al azar
    if best_move is None:
        moves = valid_movements(board, player)
        return random.choice(moves) if moves else None

    return best_move