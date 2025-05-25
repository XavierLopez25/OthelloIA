import time

import streamlit as st
import pandas as pd
import random
import numpy as np
import time
import requests

host = 'http://localhost:8000'
#host = 'http://ec2-34-204-14-38.compute-1.amazonaws.com'

st.session_state.game_id = st.session_state.get('game_id', '')
st.session_state.game_status = st.session_state.get('game_id', 'new')
st.session_state.session_status = st.session_state.get('session_status', 'open')
st.session_state.classification = st.session_state.get('classification', [])
st.session_state.matches = st.session_state.get('matches', [])

def start_game(game_id):
    if not game_id:
        st.toast('Empty text input', icon="⚠️")
        return

    # guarda en session_state el valor del input
    st.session_state.game_id = game_id

    # consulta al servidor
    game_info = requests.post(f"{host}/game/game_info?session_name={game_id}").json()
    if game_info['status'] == 501:
        # sesión nueva
        st.session_state.game_status = 'New Game'
        requests.post(f"{host}/game/new_game?session_name={game_id}")

    # carga clasificación inicial
    resp = requests.post(f"{host}/game/classification?session_name={game_id}").json()
    st.session_state.classification = resp.get('data', [])

def refresh_classif(game_id):
    response = requests.post(host + '/game/classification?session_name=' + _game_id).json()
    if 'data' in response:
        st.session_state.classification = response['data']
    else:
        st.session_state.classification = []

def remove_player(game_id, player_id):
    if game_id == '' :
        pass
    elif player_id == '' and game_id != '':
        st.toast('Empty text input', icon="⚠️")
    else:
        response = requests.post(host + '/session/eject?session_name=' + game_id + '&player_name=' + player_id).json()
        refresh_classif(game_id)

def get_boards(session_name):
    try:
        url = f"{host}/game/boards?session_name={session_name}"
        resp = requests.post(url, timeout=5)
        resp.raise_for_status()
        return resp.json()  # debería ser {'status':200,...,'data':[...]}

    except Exception as e:
        st.error(f"Error fetching boards: {e}")
        # Siempre devolvemos un dict con 'data' aunque esté vacío
        return {'data': []}
    
def display_boards(boards):
    for board_info in boards:
        st.subheader(f"Match ID: {board_info['match_id']}")
        st.write(f"White Player (⬤): {board_info['white_player']} - Score: {board_info['white_score']} | Black Player (◯): {board_info['black_player']} - Score: {board_info['black_score']}")
        
        # Convert board to DataFrame and replace values
        board = pd.DataFrame(board_info["board"])
        board = board.replace({0: "", -1: "◯", 1: "⬤"})
        
        st.table(board)

def display_boards_side_by_side(boards):
    cols = st.columns(4)  # Adjust the number of columns here
    for i, board_info in enumerate(boards):
        col = cols[i % 4]  # Use modulo to alternate columns
        with col:
            if board_info['game_over']:
                st.subheader(f"Match ID: {board_info['match_id']} 🟢")
            else:
                st.subheader(f"Match ID: {board_info['match_id']} 🟡")
            st.write(f"White Player (⬤): {board_info['white_player']} - Score: {board_info['white_score']}")
            st.write(f"Black Player (◯): {board_info['black_player']} - Score: {board_info['black_score']}")
            if board_info['game_over']:
                if board_info['black_score'] > board_info['white_score']:
                    st.write(f"¡Winner: {board_info['black_player']} ◯!")
                else:
                    st.write(f"¡Winner: {board_info['white_player']} ⬤!")
            
            # Convert board to DataFrame and replace values
            board = pd.DataFrame(board_info["board"])
            board = board.replace({0: "", -1: "◯", 1: "⬤"})
            
            st.table(board)

def refresh_matches():
    pass

def close_session():

    if st.session_state.session_status == 'open':
        st.session_state.session_status = 'close'
        close_session = requests.post(host + '/game/close_registration?session_name=' + st.session_state.game_id)
    else:
        st.session_state.session_status = 'open'
        close_session = requests.post(host + '/game/open_registration?session_name=' + st.session_state.game_id)



def pair_players():
    pair = requests.post(host+ '/game/pair_players?session_name=' + st.session_state.game_id)

st.set_page_config(page_title='Othello Game', page_icon='🎲', layout='wide', initial_sidebar_state='auto')



_game_id = st.text_input('Enter game id')

st.button(
    'Start game',
    on_click=start_game,
    args=(_game_id,),
    kwargs={},  # si no usas kwargs
)


st.title(f'{st.session_state.game_id}')

col1, col2,col3 = st.columns([4,10,2])

with col1:
    st.subheader('Classification')
with col2:
    if st.button('Clear Scores and Matches', key = 'clear_scores'):
        response = requests.post(host + '/game/clear_scores_and_matches?session_name=' + st.session_state.game_id)
        if response.status_code == 200:
            response = response.json()
            if 'data' in response:
                st.session_state.classification = response['data']
            else:
                st.session_state.classification = []
with col3:
    if st.button('Refresh', key = 'classif_refresh'):
        response = requests.post(host + '/game/classification?session_name=' + st.session_state.game_id)
        if response.status_code == 200:
            response = response.json()
            if 'data' in response:
                st.session_state.classification = response['data']
            else:
                st.session_state.classification = []


st.dataframe(
    pd.DataFrame(st.session_state.classification)
    , column_config={
            "name" : "Player"
            , "played" : st.column_config.NumberColumn('Played')
            , "wins" : st.column_config.NumberColumn('Won 🥇', format = '%d')
            , "draws" : st.column_config.NumberColumn('Drawn 🤝', format = '%d')
            , "losses" : st.column_config.NumberColumn('Lost 😿', format = '%d')
            , "points" : st.column_config.NumberColumn('Points 🏆')
        }
        , use_container_width=True
        , hide_index=True
)

_remove_player = st.text_input('Remove player')

remove_button = st.button('Remove player', on_click=remove_player(_game_id, _remove_player))

st.subheader('Matches')

col1, col2, col3= st.columns([4,10,2])


with col1:
    # pair_button = st.button('Pair', key = 'pairing', type = 'primary',  on_click = pair_players())
    if st.button('Pair', key = 'pairing', type = 'primary'):
        if st.session_state.game_id ==  '':
            st.toast('Invalid Game ID', icon="⚠️")
        else:
            pair = requests.post(host + '/game/pair_players?session_name=' + st.session_state.game_id)
            response = requests.post(host + '/game/current_matches?session_name=' + st.session_state.game_id).json()
            st.session_state.matches = response['data']

with col3:
    if st.button('Refresh', key = 'matches_refresh'):
        if st.session_state.game_id ==  '':
            st.toast('Invalid Game ID', icon="⚠️")
        else:
            response = requests.post(host + '/game/current_matches?session_name=' + st.session_state.game_id).json()
            st.session_state.matches = response['data']

st.dataframe(
    pd.DataFrame(st.session_state.matches)
    , column_config={
            "name" : "Player"
            , "played" : st.column_config.NumberColumn('Played')
            , "wins" : st.column_config.NumberColumn('Won 🥇', format = '%d')
            , "draws" : st.column_config.NumberColumn('Drawn 🤝', format = '%d')
            , "losses" : st.column_config.NumberColumn('Lost 😿', format = '%d')
            , "points" : st.column_config.NumberColumn('Points 🏆')
        }
    , use_container_width=True
    , hide_index=True
)

st.header("Othello Game Boards")

# Refresh and display the boards every few seconds if a session is active
# Button to start/stop visualization
if st.button("Toggle Visualization"):
    st.session_state['visualize'] = not st.session_state.get('visualize', False)

# Display boards if visualization is enabled
if st.session_state.get("visualize", False):
    st.subheader(f"Current Boards for Session: {st.session_state.game_id}")
    board_placeholder = st.empty()
    # If all games are done, continue the loop but stop refreshing the boards
    all_done = False
    boards = get_boards(st.session_state.game_id)['data']
    with board_placeholder.container():
        display_boards_side_by_side(boards)


    # Run visualization loop
    while st.session_state['visualize']:
        if not all_done:
            boards = get_boards(st.session_state.game_id)['data']
        
            with board_placeholder.container():
                display_boards_side_by_side(boards)

        for board_info in boards:
            #Check if all games are done
            if board_info['game_over']:
                all_done = True
            else:
                all_done = False
                break
       

        # Refresh every second
        
        time.sleep(1)

        # Check if button was clicked again to stop visualization
        if not st.session_state['visualize']:
            break