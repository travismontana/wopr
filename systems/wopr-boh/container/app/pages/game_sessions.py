import streamlit as st

from lib.helpers import debug_log, debug_json
from lib.game_sessions import create_game_session

st.header("Game Sessions Management")
st.subheader("Create New Game Session")

if "game_session" not in st.session_state:
    st.session_state["game_session"] = None
if "round_number" not in st.session_state:
    st.session_state["round_number"] = 1

if not st.session_state.get("game_session"):
    number_of_players = st.number_input(
        "Number of players:",
        min_value=3,
        max_value=6,
        value=3,
    )

    with st.form("create_game_session_form"):
        players_dict = {}
        st.divider()
        st.subheader("Player 1 Details")
        player1_name = st.text_input("Player 1 Name:", value="Player1")
        
        players_dict = {"Player 1": player1_name}
        

        for i in range(2, number_of_players + 1):
            st.subheader(f"Player {i} Details")
            player_name = st.text_input(f"Player {i} Name:", value=f"Player{i}")
            players_dict[f"Player {i}"] = player_name
        note = st.text_area("Session Note (optional):", value="First game session")
        submitted = st.form_submit_button("Create Game Session")
        
        if submitted:
            st.session_state.game_session = players_dict
            st.session_state.game_session_uuid = create_game_session(note)
            st.rerun()
else:
    
    if "round_number" not in st.session_state:
        st.session_state["round_number"] = 1
    round_number = st.session_state["round_number"]
    players_dict = st.session_state.game_session
    st.subheader("Current Game Session Players")
    st.write(f"Number of Players: {len(players_dict)}")
    st.write("Player Details:")
    st.dataframe(players_dict)
    st.divider()
    if st.button(f"Start of round {round_number}"):
        results = capture_move("round",f"start_round_{round_number}")
    for player, name in players_dict.items():
        st.write(f"{player} Name: {name}")
        move1 = st.text_input(f"{name}'s Move:",f"{name}_first_move", key=f"{name}_first_move", disabled=True)
        if st.button("Start of turn capture", key=f"{name}_capture_move"): 
            results = capture_move(name, move1)
        move2 = st.text_input(f"{name}'s Move:",f"{name}_second_move", key=f"{name}_second_move", disabled=True)
        if st.button("End of turn capture", key=f"{name}_capture_move_end"):
            results = capture_move(name, move2)
    if st.button("End of round "):
        results = capture_move("round",f"end_round_{round_number}")
        st.session_state["round_number"] += 1
