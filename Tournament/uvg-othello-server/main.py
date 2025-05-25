from fastapi import FastAPI, HTTPException
from models import TournamentCreate, UserJoin, MatchResult, UserMove
from db import db
from othello_logic import valid_movements, move, check_board_status
import random

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/tournament/create")
def create_tournament(tournament: TournamentCreate):
    existing = db.tournaments.find_one({"name": tournament.name})
    if existing:
        raise HTTPException(status_code=400, detail="Tournament already exists")
    db.tournaments.insert_one({
        "name": tournament.name
        , "players": []
        , "matches": []
        , "status": "available"
    })
    return {"msg": "Tournament created"}

@app.post("/tournament/close")
def close_tournament(tournament: TournamentCreate):
    tournament_reg = db.tournaments.find_one({"name": tournament.name})
    if not tournament_reg:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament_reg["status"] == "closed":
        raise HTTPException(status_code=400, detail="Tournament is already closed")

    db.tournaments.update_one(
        {"name": tournament.name},
        {"$set": {"status": "closed"}}
    )
    return {"msg": f"Tournament {tournament.name} is now closed"}

@app.get("/tournament/available")
def get_available_tournaments():
    cursor = db.tournaments.find({"status": "available"}, {"_id": 0, "name": 1})
    tournaments = list(cursor)
    names = [t["name"] for t in tournaments]
    return {"available_tournaments": names}


@app.post("/tournament/join")
def join_tournament(user: UserJoin):
    tournament = db.tournaments.find_one({"name": user.tournament_name})
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    for player in tournament["players"]:
        if user.username == player['name']:
            raise HTTPException(status_code = 409, detail = f"Username {user.username} already exists")

    tournament["players"].append({
        'name' : user.username
        , 'wins' : 0
        , 'draws' : 0 
        , 'loses' : 0
        , 'pieces_diff' : 0 
    })

    db.tournaments.update_one(
        {"name": user.tournament_name},
        {"$set": {"players": tournament["players"]}}
    )
    return {"msg": f"{user.username} joined {user.tournament_name}"}

@app.post("/pair/")
def pair_players(tournament_name: str):
    tournament = db.tournaments.find_one({"name": tournament_name})
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    # Check if all matches have ended
    ongoing_matches = db.boards.find_one({"status": "ongoing", "tournament_name": tournament_name})
    if ongoing_matches:
        raise HTTPException(status_code=400, detail="Cannot pair players while matches are still ongoing")

    players = tournament["players"]
    if len(players) < 2:
        raise HTTPException(status_code=400, detail="Not enough players to pair")

    matches = []

    while len(players) > 1:
        black_player = players.pop(random.randint(0, len(players) - 1))
        white_player = players.pop(random.randint(0, len(players) - 1))
        board = [[0]*8 for _ in range(8)]
        board[3][3] = 1     # White
        board[3][4] = -1    # Black
        board[4][3] = -1    # Black
        board[4][4] = 1 
        match_doc = {
            'black_player': black_player,
            'white_player': white_player,
            "board": board,
            "status": "ongoing",
            "turn": "black",
            "black_strikes": 0,
            "white_strikes": 0,
            "tournament_name": tournament_name
        }
        db.boards.insert_one(match_doc)
        matches.append(match_doc)

    bench = []
    if len(players) == 1:
        bench = players
    db.tournaments.update_one(
        {"name": tournament_name},
        {"$set": {"bench": bench}}
    )

    return {"msg": "Players paired",}

@app.post("/match/status")
def get_match_status(user: UserJoin):
    tournament = db.tournaments.find_one({"name": user.tournament_name})
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    match = db.boards.find_one({
        "$or": [
            {"black_player.name": user.username},
            {"white_player.name": user.username}
        ],
        "status": "ongoing"
        , "tournament_name" : user.tournament_name
    })
    if not match:
        raise HTTPException(status_code=404, detail="No ongoing match found for the user")

    # Check if the match is over
    match_status = check_board_status(match["board"])
    if match_status['status'] == "ended":
        print(match_status)
        black_score = match_status['black']
        white_score = match_status['white']
        winner = match_status["winner"]

        for player in tournament["players"]:
            if player["name"] == match["black_player"]["name"]:
                if winner == "black":
                    player["wins"] += 1
                elif winner == "white":
                    player["loses"] += 1
                else:
                    player["draws"] += 1
                player["pieces_diff"] += black_score - white_score
            elif player["name"] == match["white_player"]["name"]:
                if winner == "white":
                    player["wins"] += 1
                elif winner == "black":
                    player["loses"] += 1
                else:
                    player["draws"] += 1
                player["pieces_diff"] += white_score - black_score

        db.tournaments.update_one(
            {"name": user.tournament_name},
            {"$set": {"players": tournament["players"]}}
        )

        db.boards.update_one(
            {"_id": match["_id"]},
            {"$set": {"status": "ended", "winner": winner, "black_score" : black_score, "white_score" : white_score}}
        )

        return {"msg": "Match ended", "winner": winner, "board": match["board"]}

    # If the match is ongoing, keep the existing logic
    current_turn = match["turn"]
    
    if (current_turn == "black" and match["black_player"]["name"] != user.username) or (current_turn == "white" and match["white_player"]["name"] != user.username):
        raise HTTPException(status_code=409, detail="Is not your turn")
        # return {"msg": "IS NOT YOUR TURN", "board": []}

    player_color = -1 if match["black_player"]["name"] == user.username else 1
    return {"msg": "YOUR TURN", "board": match["board"], "player_color": player_color}

@app.post("/match/active")
def is_user_in_active_match(user: UserJoin):
    tournament = db.tournaments.find_one({"name": user.tournament_name})
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    match = db.boards.find_one({
        "$or": [
            {"black_player.name": user.username},
            {"white_player.name": user.username}
        ],
        "status": "ongoing",
        "tournament_name": user.tournament_name
    })
    return {"is_in_active_match": bool(match)}

@app.post("/match/valid-movements")
def get_valid_movements(user: UserJoin):
    tournament =  db.tournaments.find_one({"name": user.tournament_name})
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    match = db.boards.find_one({
        "$or": [
            {"black_player.name": user.username},
            {"white_player.name": user.username}
        ],
        "status": "ongoing"
    })
    if not match:
        raise HTTPException(status_code=404, detail="No ongoing match found for the user")

    current_turn = match["turn"]
    if (current_turn == "black" and match["black_player"]["name"] != user.username) or (current_turn == "white" and match["white_player"]["name"] != user.username):
        raise HTTPException(status_code=400, detail="Not your turn")

    player_color = 1 if current_turn == "white" else -1
    valid_moves = valid_movements(match["board"], player_color)

    return {"valid_movements": valid_moves}

@app.post("/match/move")
def make_move(movement: UserMove):
    tournament = db.tournaments.find_one({"name": movement.tournament_name})
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    match = db.boards.find_one({
        "$or": [
            {"black_player.name": movement.username},
            {"white_player.name": movement.username}
        ],
        "status": "ongoing"
        , "tournament_name" : movement.tournament_name
    })
    if not match:
        raise HTTPException(status_code=404, detail="No ongoing match found for the user")

    current_turn = match["turn"]
    if (current_turn == "black" and match["black_player"]["name"] != movement.username) or (current_turn == "white" and match["white_player"]["name"] != movement.username):
        raise HTTPException(status_code=400, detail="Not your turn")

    player_color = 1 if current_turn == "white" else -1
    valid_moves = valid_movements(match["board"], player_color)

    if (movement.x, movement.y) not in valid_moves:
        raise HTTPException(status_code=409, detail="Invalid Movement")

    updated_board = move(match["board"], player_color, movement.x, movement.y)
    opponent_color = 1 if current_turn == "black" else -1
    opponent_valid_moves = valid_movements(updated_board, opponent_color)
    if opponent_valid_moves:
        next_turn = "white" if current_turn == "black" else "black"
    else:
        next_turn = current_turn

    db.boards.update_one(
        {"_id": match["_id"]},
        {"$set": {"board": updated_board, "turn": next_turn}}
    )

    return {"msg": "Move accepted"}

@app.get("/tournament/players/{tournament_name}")
def get_tournament_players(tournament_name: str):
    tournament = db.tournaments.find_one({"name": tournament_name})
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    players = tournament.get("players", [])
    return {"players": players}

@app.get("/leaderboard/{tournament_name}")
def get_leaderboard(tournament_name: str):
    cursor = db.leaderboard.find({"tournament": tournament_name})
    leaderboard = list(cursor)
    leaderboard.sort(key=lambda x: (-x["points"], -x["piece_diff"]))
    return leaderboard

@app.get("/tournament/matches/{tournament_name}")
def get_ongoing_matches(tournament_name: str):
    tournament = db.tournaments.find_one({"name": tournament_name})
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    cursor = db.boards.find({"tournament_name": tournament_name})
    matches = list(cursor)
    for match in matches:
        match["_id"] = str(match["_id"])  # Convert ObjectId to string
    return {"matches": matches}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)