from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import string
import random
import json
import os
import pickle
from othello_game import OthelloGame

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[""]
)

othello_session_data_structure = {
    'status' : 'active'
    , 'registration' : 'open'
    , 'round' : 'hold'
    , 'players' : []
    , 'league' : []
    # league[{player, wins, loses, ties, points}]
}

### API Management

@app.get("/root")
def read_root():
    return {'Status': 'Contemplating existence. Also, kind of active.'}

### Game Management

def active_games(session_name):
    pass


@app.post("/game/new_game")
def new_game(session_name : str):
    _session_path = '../sessions/' + session_name
    if not(os.path.exists(_session_path)):
        os.makedirs(_session_path, exist_ok=True)
        if os.path.exists(_session_path):
            file_path = _session_path + '/session_variables.json'
            with open(file_path, 'w') as file:
                json.dump(othello_session_data_structure, file)
            os.makedirs(_session_path + '/games', exist_ok=True)
            return {
                'status' : 200
                , 'message' : 'New game has been created.'
            }
        else:
            return {
                'status': 502
                , 'message': 'ERROR creating new game'
            }

    else:
        return {
            'status' : 501
            , 'message' : session_name + ' already exists.'
        }

@app.post("/game/close_registration")
def close_gamge(session_name : str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        data['registration'] = 'close'
        with open(file_path, 'w') as file:
            json.dump(data, file)

        return {
            'status': 200
            , 'message': 'Session has been closed.'
        }
    else:
        return {
            'status' : 501
            , 'message' : 'Session ID does not exist.'
        }

@app.post("/game/open_registration")
def open_game(session_name : str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        data['registration'] = 'open'
        with open(file_path, 'w') as file:
            json.dump(data, file)

        return {
            'status': 200
            , 'message': 'Session has been open.'
        }
    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
        }

@app.post("/game/game_info")
def open_game(session_name : str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        if ('current_matches' in data) & (data['round'] == 'ready'):
            if all(d.get('status') == 'done' for d in data['current_matches']):
                data['round'] = 'hold'


                for match in data['current_matches']:
                    game_path = _session_path + '/games/' + match['match_id'] + '.pkl'
                    with open(game_path, 'rb') as f:
                        othello_game = pickle.load(f)

                    _winner = othello_game.winner
                    _whites = match['whites']
                    _blacks = match['blacks']

                    for index, _player in enumerate(data['league']):

                        if (_player['name'] == _whites)|(_player['name'] == _blacks):

                            if _winner == 'Tie':
                                _player['draws'] += 1
                            else:
                                if _player['name'] == _winner:
                                    _player['wins'] += 1
                                else:
                                    _player['losses'] += 1

                            _player['points'] = (_player['wins']  * 3) + (_player['draws'])

                        data['league'][index] = _player


                with open(file_path, 'w') as file:
                     json.dump(data, file)

        return {
            'status': 200
            , 'message': 'Session status retrieved successfully.'
            , 'session_status' : data['status']
            , 'round_status': data['round']
        }
    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
        }

def random_pair(items):
    _random_items = random.sample(items, len(items))
    pairs = []
    for i in range(0, len(_random_items) - 1, 2):
        pairs.append([_random_items[i], _random_items[i+1]])
    if len(_random_items) % 2 != 0:
        pairs.append([_random_items[-1],])
    return pairs

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.post("/game/pair_players")
def pair_players(session_name : str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        if data['registration'] == 'not applicable any more':
            return {
                'status': 502
                , 'message': 'Session must be closed to pair players'
            }
        else :
            _players = data['players']
            _random_pairs = random_pair(_players)
            _matches = []
            _benched = []
            for pair in _random_pairs:
                if len(pair) == 2:
                    match_id = generate_random_string(10)
                    _matches.append({
                        'match_id': match_id
                        , 'whites': pair[0]
                        , 'blacks': pair[1]
                        , 'status' : 'active'
                    })

                    game_path = _session_path + '/games/' + match_id + '.pkl'
                    othello_game = OthelloGame(match_id, pair[0], pair[1])
                    with open(game_path, 'wb') as f:
                        # Serialize and save the object to the file
                        pickle.dump(othello_game, f)

                else:
                    _benched.append(pair[0])
            data['current_matches'] = _matches
            data['bench'] = _benched

            data['round'] = 'ready'

            with open(file_path, 'w') as file:
                json.dump(data, file)

            return {
                'status': 200
                , 'message': 'Players paired successfully'
            }
    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
        }

### Player Management

@app.post("/player/new_player")
def new_player(session_name : str, player_name : str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        if player_name not in data['players']:
            data['players'].append(player_name)

            name_exists = any(player['name'] == player_name for player in data['league'])

            if not name_exists:
                data['league'].append({
                    'name': player_name
                    , 'wins': 0
                    , 'draws': 0
                    , 'losses': 0
                    , 'points' : 0
                })

            with open(file_path, 'w') as file:
                json.dump(data, file)
            return {
                'status': 200
                , 'message': 'Player created successfully'
            }
        else :
            return {
                'status': 502
                , 'message': 'User name not available'
            }
    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
        }

@app.post("/player/match_info")
def match_info(session_name : str, player_name: str):

    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        if data['round'] == 'ready':

            if player_name in data['bench']:
                return {
                    'status': 200
                    , 'message': 'Match info retrieved successfully'
                    , 'player_name': player_name
                    , 'match' : 'bench'
                    , 'symbol' : 0
                    , 'match_status' : 'bench'
                }
            else:
                if 'current_matches' in data:
                    for match in data['current_matches']:
                        if player_name == match['whites']:

                            return {
                                'status': 200
                                , 'message': 'Match info retrieved successfully'
                                , 'player_name': player_name
                                , 'match': match['match_id']
                                , 'symbol': 1
                                , 'match_status' : match['status']
                            }
                        if player_name == match['blacks']:
                            return {
                                'status': 200
                                , 'message': 'Match info retrieved successfully'
                                , 'player_name': player_name
                                , 'match': match['match_id']
                                , 'symbol': -1
                                , 'match_status' : match['status']
                            }

                return {
                    'status': 502
                    , 'message': 'Missing Player'
                }
        if data['round'] == 'hold':
            return {
                'status': 200
                , 'message': 'Match info retrieved successfully'
                , 'player_name': player_name
                , 'match': 'None'
                , 'symbol': 0
                , 'match_status': 'None'
            }
    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
        }


@app.post("/player/turn_to_move")
def turn_to_move(session_name : str, player_name : str, match_id : str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        if player_name in data['players']:
            if player_name in data['bench']:
                return {
                    'status': 200
                    , 'message': 'You are currently benched in this session'
                    , 'turn'  : False
                }

            if 'current_matches' in data:
                for match in data['current_matches']:

                    if ((player_name == match['whites']) | (player_name == match['blacks'])) & (match['match_id'] == match_id):
                        game_path = _session_path + '/games/' + match_id + '.pkl'
                        with open(game_path, 'rb') as f:
                            othello_game = pickle.load(f)

                        if (othello_game.current_player == 1) and (player_name == match['whites']):
                            return {
                                'status': 200
                                , 'message': 'White Move'
                                , 'turn' : True
                                , 'game_over' : othello_game.game_over
                                , 'winner' : othello_game.winner
                                , 'board' : othello_game.board
                                , 'score' : 'Whites : ' + str(othello_game.score[1]) + ' - Blacks : ' + str(othello_game.score[-1])
                            }
                        else :
                            if (othello_game.current_player == -1) and (player_name == match['blacks']):
                                return {
                                    'status': 200
                                    , 'message': 'Black Move'
                                    , 'turn' : True
                                    , 'game_over': othello_game.game_over
                                    , 'winner': othello_game.winner
                                    , 'board': othello_game.board
                                    , 'score' : 'Whites : ' + str(othello_game.score[1]) + ' - Blacks : ' + str(othello_game.score[-1])
                                }
                            else :
                                return {
                                    'status': 200
                                    , 'message': 'White Move' if othello_game.current_player == 1 else 'Black Move'
                                    , 'turn': False
                                    , 'game_over': othello_game.game_over
                                    , 'winner': othello_game.winner
                                    , 'score' : 'Whites : ' + str(othello_game.score[1]) + ' - Blacks : ' + str(othello_game.score[-1])
                                }
            return {
                'status': 503
                , 'message': 'Invalid User name - Match ID combination'
            }
        else:
            return {
                'status': 502
                , 'message': 'Invalid User name'
            }

    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
        }

    # return {
    #         'game_status' : 'keep playing'
    #         , 'message' : 'Turn to move'
    #     }

@app.post("/player/move")
def move_coin(session_name : str, player_name : str, match_id : str, row : int, col : int):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        if player_name in data['players']:
            if player_name in data['bench']:
                return {
                    'status': 200
                    , 'message': 'You are currently benched in this session'
                    , 'turn'  : False
                }

            for index, match in enumerate(data['current_matches']):

                if ((player_name == match['whites']) or (player_name == match['blacks'])) and (match['match_id'] == match_id):
                    game_path = _session_path + '/games/' + match_id + '.pkl'
                    with open(game_path, 'rb') as f:
                        othello_game = pickle.load(f)

                    if ((othello_game.current_player == 1) & (player_name == match['whites'])) | ((othello_game.current_player == -1) & (player_name == match['blacks'])):

                        flag, msg = othello_game.update_board(othello_game.current_player, row, col)
                        if flag:

                            if othello_game.game_over:
                                data['current_matches'][index]['status'] = 'done'
                                with open(file_path, 'w') as file:
                                    json.dump(data, file)

                            with open(game_path, 'wb') as f:
                                pickle.dump(othello_game, f)
                            return {
                                'status': 200
                                , 'message' : 'Piece moved successfully.'
                            }
                        else :
                            if msg == 'INVALID':
                                othello_game.strike()

                                with open(game_path, 'wb') as f:
                                    pickle.dump(othello_game, f)

                                return {
                                    'status': 504
                                    , 'message': 'Invalid Move'
                                }

                            else:

                                return {
                                    'status': 401
                                    , 'message': 'Lost by overtime'
                                }

            return {
                'status': 503
                , 'message': 'Invalid User name - Match ID combination'
            }
        else:
            return {
                'status': 502
                , 'message': 'Invalid User name'
            }

    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
        }

@app.post("/game/classification")
def league_info(session_name: str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        return {
            'status': 200
            , 'message': 'Classification retrieved successfully.'
            , 'data' : data['league']
        }
    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
            , 'data': []
        }

@app.post("/game/end_match")
def end_match(session_name : str, match_id : str, player_name : str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        game_path = _session_path + '/games/' + match_id + '.pkl'
        with open(game_path, 'rb') as f:
            othello_game = pickle.load(f)

        othello_game.game_over = True
        othello_game.winner = player_name

        with open(game_path, 'wb') as f:
            pickle.dump(othello_game, f)

        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        for index, _match in enumerate(data['current_matches']):
            if _match['match_id'] == match_id:
                _match['status'] = 'done'
                data['current_matches'][index] = _match

                with open(file_path, 'w') as file:
                    json.dump(data, file)

        return {
            'status' : 200
            , 'message' : 'Game end succesfully'
        }

    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
        }

@app.post("/session/eject")
def eject_player(session_name : str, player_name : str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        
        if player_name in data['players']:
            data['players'].remove(player_name)
            
            data['league'] = [player for player in data['league'] if player['name'] != player_name]
            print(data)
            with open(file_path, 'w') as file:
                json.dump(data, file)

            return {
                'status' : 200
                , 'message' : 'Player removed successfully'
            }
        else:
            return {
                'status' : 502
                , 'message' : 'Player not in specified session'
            }

    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
            , 'data': []
        }

@app.post("/game/current_matches")
def matches_info(session_name: str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        _current_matches = []
        for match in data['current_matches']:
            game_path = _session_path + '/games/' + match['match_id'] + '.pkl'
            with open(game_path, 'rb') as f:
                othello_game = pickle.load(f)

            match['white_score'] = othello_game.score[1]
            match['black_score'] = othello_game.score[-1]

            _current_matches.append(match)
        return {
            'status': 200
            , 'message': 'Classification retrieved successfully.'
            , 'data' : _current_matches
        }
    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
            , 'data': []
        }
    

@app.post("/game/boards")
def board_info(session_name : str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        _boards = []
        for match in data['current_matches']:
            game_path = _session_path + '/games/' + match['match_id'] + '.pkl'
            with open(game_path, 'rb') as f:
                othello_game = pickle.load(f)

            _boards.append({
                'match_id' : othello_game.gameid
                , 'white_player' : othello_game.white_player
                , 'black_player' : othello_game.black_player
                , 'board' : othello_game.board
                , 'white_score' : othello_game.score[1]
                , 'black_score' : othello_game.score[-1]
                , 'game_over' : othello_game.game_over
            })

        return {
            'status': 200
            , 'message': 'Boards retrieved successfully.'
            , 'data': _boards
        }

@app.post("/game/clear_scores_and_matches")
def clear_scores(session_name : str):
    _session_path = '../sessions/' + session_name
    if os.path.exists(_session_path):
        file_path = _session_path + '/session_variables.json'
        with open(file_path, 'r') as file:
            data = json.load(file)

        for index, player in enumerate(data['league']):
            player['wins'] = 0
            player['draws'] = 0
            player['losses'] = 0
            player['points'] = 0
            data['league'][index] = player
        
        data['current_matches'] = []

        with open(file_path, 'w') as file:
            json.dump(data, file)

        #remove all games
        games_path = _session_path + '/games'
        for game in os.listdir(games_path):
            game_path = games_path + '/' + game
            os.remove(game_path)

        return {
            'status': 200
            , 'message': 'Scores cleared successfully.'
            , 'data': data['league']
        }
    else:
        return {
            'status': 501
            , 'message': 'Session ID does not exist.'
        }
    



        


# return {
    #     'message' : 'Coin moved successfully.'
    # }

# @app.post("/match/status")
# def match_status(session_name : str, match_id : str):
#     return {
#         'status' : 'on going'
#         , 'message' : 'Match status retrieved successfully.'
#     }