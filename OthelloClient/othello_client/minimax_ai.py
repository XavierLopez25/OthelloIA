import math
import time
from random_ia import valid_moves  # tus movimientos válidos ya definidos

# 1) Tabla de posición de discos
DISC_SQUARE_TABLE = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   0,   0,   0,   0,  -2,  10],
    [  5,  -2,   0,   0,   0,   0,  -2,   5],
    [  5,  -2,   0,   0,   0,   0,  -2,   5],
    [ 10,  -2,   0,   0,   0,   0,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]

# 2) Factores de evaluación
def coin_parity(board, player):
    my  = sum(cell == player   for r in board for cell in r)
    opp = sum(cell == -player  for r in board for cell in r)
    return 0 if my+opp == 0 else 100*(my-opp)/(my+opp)

def mobility(board, player):
    my  = len(valid_moves(board, player))
    opp = len(valid_moves(board, -player))
    return 0 if my+opp == 0 else 100*(my-opp)/(my+opp)

def count_frontier_discs(board, player):
    directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    frontier = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == player:
                for dr, dc in directions:
                    rr, cc = r+dr, c+dc
                    if 0<=rr<8 and 0<=cc<8 and board[rr][cc]==0:
                        frontier += 1
                        break
    return frontier

def disc_square_score(board, player):
    total = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == player:
                total += DISC_SQUARE_TABLE[r][c]
            elif board[r][c] == -player:
                total -= DISC_SQUARE_TABLE[r][c]
    return total

def stability(board, player):
    corners = [(0,0),(0,7),(7,0),(7,7)]
    my = sum(board[r][c]==player  for r,c in corners)
    op = sum(board[r][c]==-player for r,c in corners)
    return 0 if my+op==0 else 100*(my-op)/(my+op)

# 3) La función evaluate que combina todo
def evaluate(board, player):
    # pesos típicos (ajústalos tras pruebas)
    w_parity    = 10
    w_mobility  = 78
    w_frontier  = 74
    w_square    = 10
    w_stability = 801

    return (
        w_parity    * coin_parity(board, player)
      + w_mobility  * mobility(board, player)
      - w_frontier  * count_frontier_discs(board, player)
      + w_square    * disc_square_score(board, player)
      + w_stability * stability(board, player)
    )

def minimax(board, player, depth, alpha, beta, maximizing, opponent, start, time_limit=3, is_root=True):
    # Si nos quedamos sin tiempo
    if time.time() - start > time_limit:
        raise TimeoutError()
    # Terminal o profundidad 0
    moves = valid_moves(board, player if maximizing else opponent)
    if depth == 0 or not moves:
        return evaluate(board, player), None

    best_move = None
    if maximizing:
        value = -math.inf
        for mv in moves:
            newb = [r[:] for r in board]
            apply_move(newb, player, mv)
            v, _ = minimax(newb, player, depth-1, alpha, beta, False, opponent, start, time_limit, is_root=False)
            if v > value:
                value, best_move = v, mv
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        if is_root:
            print("Tiempo de la jugada:", time.time() - start)
        return value, best_move
    else:
        value = math.inf
        for mv in moves:
            newb = [r[:] for r in board]
            apply_move(newb, opponent, mv)
            v, _ = minimax(newb, player, depth-1, alpha, beta, True, opponent, start, time_limit, is_root=False)
            if v < value:
                value, best_move = v, mv
            beta = min(beta, value)
            if alpha >= beta:
                break
        if is_root:
            print("Tiempo de la jugada:", time.time() - start)
        return value, best_move

def apply_move(board, player, move):
    """
    Replica la lógica de OthelloGame.update_board:
    coloca la ficha y voltea en todas direcciones.
    """
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]
    r0, c0 = move
    board[r0][c0] = player
    opponent = -player
    for dr, dc in DIRECTIONS:
        r, c = r0 + dr, c0 + dc
        flip = []
        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
            flip.append((r, c))
            r += dr; c += dc
        if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
            for (fr, fc) in flip:
                board[fr][fc] = player