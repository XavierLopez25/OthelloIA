import math
import time
import random

# --- 1) Importas tu función existente de movimientos válidos ---
from othello_ai import valid_movements  # si tuvieras que cambiar el nombre de módulo, ajústalo aquí

# --- 2) Tabla de posición de discos (Disc-Square Table) ---
DISC_SQUARE_TABLE = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,    0,   0,   0,   0,  -2,  10],
    [  5,  -2,    0,   0,   0,   0,  -2,   5],
    [  5,  -2,    0,   0,   0,   0,  -2,   5],
    [ 10,  -2,    0,   0,   0,   0,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]

# --- 3) Funciones de evaluación ---
def coin_parity(board, player):
    my  = sum(cell == player   for row in board for cell in row)
    opp = sum(cell == -player  for row in board for cell in row)
    return 0 if (my+opp)==0 else 100*(my-opp)/(my+opp)

def mobility(board, player):
    my  = len(valid_movements(board, player))
    opp = len(valid_movements(board, -player))
    return 0 if (my+opp)==0 else 100*(my-opp)/(my+opp)

def count_frontier_discs(board, player):
    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    frontier = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == player:
                for dr, dc in dirs:
                    rr, cc = r+dr, c+dc
                    if 0<=rr<8 and 0<=cc<8 and board[rr][cc]==0:
                        frontier += 1
                        break
    return frontier

def disc_square_score(board, player):
    s = 0
    for r in range(8):
        for c in range(8):
            if   board[r][c] == player:   s += DISC_SQUARE_TABLE[r][c]
            elif board[r][c] == -player:  s -= DISC_SQUARE_TABLE[r][c]
    return s

def stability(board, player):
    corners = [(0,0),(0,7),(7,0),(7,7)]
    my = sum(board[r][c]==player  for r,c in corners)
    op = sum(board[r][c]==-player for r,c in corners)
    return 0 if (my+op)==0 else 100*(my-op)/(my+op)

def evaluate(board, player):
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

# --- 4) Simulación interna de la jugada (apply_move) ---
def apply_move(board, player, move):
    """
    Copia de lo que tu servidor hace: coloca la ficha y voltea
    """
    DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    newb = [row[:] for row in board]
    r0, c0 = move
    newb[r0][c0] = player
    opp = -player

    for dr, dc in DIRECTIONS:
        r, c = r0+dr, c0+dc
        path = []
        while 0<=r<8 and 0<=c<8 and newb[r][c]==opp:
            path.append((r,c))
            r += dr; c += dc
        if path and 0<=r<8 and 0<=c<8 and newb[r][c]==player:
            for (pr,pc) in path:
                newb[pr][pc] = player

    return newb

# --- 5) Minimax + α–β + Iterative Deepening + control de tiempo ---
def minimax(board, player, depth, α, β, maximizing, opponent, start, time_limit, is_root):
    if time.time() - start > time_limit:
        raise TimeoutError()
    moves = valid_movements(board, player if maximizing else opponent)
    if depth==0 or not moves:
        return evaluate(board, player), None

    best_mv = None
    if maximizing:
        value = -math.inf
        for mv in moves:
            child = apply_move(board, player, mv)
            v, _ = minimax(child, player, depth-1, α, β, False, opponent, start, time_limit, False)
            if v>value:
                value, best_mv = v, mv
            α = max(α, value)
            if α>=β: break
        if is_root:
            print(f"[Minimax] depth={depth} time={(time.time()-start):.3f}s")
        return value, best_mv

    else:
        value = math.inf
        for mv in moves:
            child = apply_move(board, opponent, mv)
            v, _ = minimax(child, player, depth-1, α, β, True, opponent, start, time_limit, False)
            if v<value:
                value, best_mv = v, mv
            β = min(β, value)
            if α>=β: break
        if is_root:
            print(f"[Minimax] depth={depth} time={(time.time()-start):.3f}s")
        return value, best_mv