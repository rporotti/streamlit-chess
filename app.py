import streamlit as st
import pandas as pd
import numpy as np
import os
import random
import itertools
import shutil
from round_robin import round_robin


GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1FUihhqQEB_sC45MXocgXWEsPyhekytZdu1oNMqbkCts/edit#gid=0"


test=True

def calculate_new_elo(df_elo, df_tournament):
    print(df_elo)
    df_tournament["Result"] = df_tournament["Result"].astype(float)
    win_white = df_tournament.groupby("White").agg({"Result": sum}).reset_index().rename(columns={"White": 'Name'})
    win_black = df_tournament.groupby("Black").agg({"Result": lambda x: 1-np.sum(x)}).reset_index().rename(columns={"Black": 'Name'})

    result_df = pd.concat([win_white, win_black]).groupby(['Name']).sum().reset_index()


    list_of_games_per_player = {}
    list_of_expected = {}
    list_of_new_elo = {}
    output = {"Name": [], "Old ELO": [], "Expected": [], "Score": [], "ELO": []}
    for player in df_tournament["White"].unique():
        list_of_games_per_player[player] = []
        list_of_expected[player] = 0

        try:
            elo_player = int(df_elo[df_elo["Name"]==player]["ELO"])
        except:
            elo_player=800
            
        for row in df_tournament.iterrows():
            if row[1]["White"]==player:
                opponent = row[1]["Black"]
            if row[1]["Black"]==player:
                opponent = row[1]["White"]
            try:
                opponent_elo = int(df_elo[df_elo["Name"]==opponent]["ELO"])
            except: 
                opponent_elo=800
            list_of_games_per_player[player].append(opponent)
            list_of_expected[player] += expected(elo_player, opponent_elo)
        score_player = int(result_df[result_df["Name"]==player]["Result"])
        new_elo = int(elo(elo_player, list_of_expected[player], score_player, k=32)   )
        list_of_new_elo[player] = new_elo
        print(f"Starting ELO of {player}: {elo_player}")
        print(f"Expected performance of {player}: {list_of_expected[player]}")
        print(f"New ELO of {player}: {new_elo}\n")
        output["Name"].append(player)
        output["Old ELO"].append(elo_player)
        output["ELO"].append(new_elo)
        output["Expected"].append(list_of_expected[player])
        output["Score"].append(score_player)
    print(output)
    output_df = pd.DataFrame.from_dict(output)
    return output_df

def expected(A, B):
    """
    Calculate expected score of A in a match against B
    :param A: Elo rating for player A
    :param B: Elo rating for player B
    """
    return 1 / (1 + 10 ** ((B - A) / 400))


def elo(old, exp, score, k=32):
    """
    Calculate the new Elo rating for a player
    :param old: The previous Elo rating
    :param exp: The expected score for this match
    :param score: The actual score for this match
    :param k: The k-factor for Elo (default: 32)
    """
    return old + k * (score - exp)


def append_column():
    
    if st.session_state.pairings_df.columns[-1] == "Result":
        print(st.session_state.pairings_df.columns)
        st.session_state.pairings_df.rename(columns={"Result": "Result round 1"}, inplace=True)
        st.session_state.pairings_df["Result round 2"] = None
        print(st.session_state.pairings_df.columns)
    elif "Result round" in st.session_state.pairings_df.columns[-1]:
        round = st.session_state.pairings_df.columns[-1].split("Result round ")[1]
        st.session_state.pairings_df[f"Result round {round+1}"]=None
    return st.session_state.pairings_df
def save_backup():
    print(st.session_state)

def round_robin_generator(list):
    """ Create a schedule for the teams in the list and return it"""
    s = []
    if len(list) % 2 == 1: list = list + ["BYE"]
    for i in range(len(list)-1):
        mid = int(len(list) / 2)
        l1 = list[:mid]
        l2 = list[mid:]
        l2.reverse()	
        # Switch sides after each round
        if(i % 2 == 1):
            s = s + [ zip(l1, l2) ]
        else:
            s = s + [ zip(l2, l1) ]
        list.insert(1, list.pop())
    return s


def create_pairings(df, test=False):
    df = df.reset_index()
    players = df["Name"].to_list()
    


    rounds = []
    
    for index, match in enumerate(round_robin(players, method="berger")):
        for x in list(match):
            rounds.append([(index+1)]+ list(x) )
    for index, match in enumerate(round_robin(players, method="berger")):
        print(index)
        for x in list(match):
            rounds.append([(index+len(players))]+ list(x)[::-1] )
            #rounds.append([(index+1+len(players))]+ list(x)[::-1] )
    print(rounds)
    df_out = pd.DataFrame(rounds, columns=["Round", "White", "Black"])
    df_out["Result"] = None
    df_out = df_out[(df_out["White"]!="BYE") & (df_out["Black"]!="BYE")]
    df_out = df_out.sort_values("Round", ascending=True).set_index("Round")
    if st.session_state.type_tournament=="Finite amount of rounds":
       
       df_out = df_out[df_out.index<=st.session_state.number_of_rounds]
    return df_out
# Loading data:

def read_data(data_path_xlsx):
    df = pd.read_csv(data_path_xlsx)
    return df


import streamlit as st
import pandas as pd

from streamlit.components.v1 import iframe


print("Loading data")
if os.path.exists("participants.csv"):
    data = read_data("participants.csv")
    st.session_state.data = data
else:
    data = pd.DataFrame(columns=["Name", "ELO"])
    data["ELO"] = data["ELO"].astype("int")
        
st.session_state.data = data.set_index("Name")


    

#st.set_page_config(layout="centered", page_title="Data Editor", page_icon="🧮")

st.title("🧠 Guess the idiom")







left, right = st.columns(2)
with left:

    edited_df = st.experimental_data_editor(
        st.session_state.data.dropna(axis=0),
        use_container_width=False,
        num_rows="dynamic",
        on_change=save_backup,
        
    )
    edited_df = edited_df
    st.write("Number of players: ", len(edited_df))

with right:
    iframe(
            src=GOOGLE_SHEET_URL,
            height=600,
        )

st.session_state.type_tournament = st.selectbox("Tournament type", ["Round-robin", "Finite amount of rounds"])
if st.session_state.type_tournament=="Finite amount of rounds":
    col1, col2 = st.columns(2)
    st.session_state.number_of_rounds = col1.number_input('Number of rounds', min_value=1)
    #st.session_state.alternate_bw = col2.radio('Alternate BW', ("Yes", "No"))
pairings_df = create_pairings(edited_df, test=True)

st.session_state.pairings_df = st.experimental_data_editor(pairings_df)

if not np.any(st.session_state.pairings_df["Result"].isna()):
    df = calculate_new_elo(edited_df, st.session_state.pairings_df).set_index("Name")
    st.write(df)
    st.download_button("⬇️ Download dataframe as .csv", df.to_csv(), "annotated.csv")
    if st.button("Update results"):
        shutil.copy("participants.csv", ".backup/participants_backup.csv")
        open("participants.csv", 'w').write(df.reset_index()[["Name", "ELO"]].to_csv(index=False))
    #st.write(compute_expected(edited_df, st.session_state.pairings_df))
    #join = result.merge(edited_df, on="Name")
    #st.write(join)
    

    #st.expander("Edited dataset", expanded=True).dataframe(edited, use_container_width=True)
