# Direcciones para explorar en el tablero
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1),
              (-1, -1), (-1, 1), (1, -1), (1, 1)]

def is_valid_move(board, player, row, col):
    if board[row][col] != 0:
        return False
    opponent = -player
    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        found_opponent = False
        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
            r += dr; c += dc
            found_opponent = True
        if found_opponent and 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
            return True
    return False

def valid_moves(board, player):
    moves = []
    for r in range(8):
        for c in range(8):
            if is_valid_move(board, player, r, c):
                moves.append((r, c))
    return moves
