
import streamlit as st
import pandas as pd

# Constants
NUM_TEAMS = 12
BUDGET = 200
ROSTER_SIZE = 14
STARTING_LINEUP = {
    "QB": 1,
    "RB": 1,
    "WR": 1,
    "TE": 1,
    "FLEX": 2,
    "K": 1,
    "DEF": 1
}
BENCH_SLOTS = ROSTER_SIZE - sum(STARTING_LINEUP.values())

# Initialize session state
if "players" not in st.session_state:
    st.session_state.players = pd.DataFrame(columns=["Name", "Position", "Team", "ProjPoints", "AAV"])
if "drafted" not in st.session_state:
    st.session_state.drafted = pd.DataFrame(columns=["Name", "Position", "Team", "ProjPoints", "AAV", "TeamOwner", "Bid"])
if "budgets" not in st.session_state:
    st.session_state.budgets = {f"Team {i+1}": BUDGET for i in range(NUM_TEAMS)}
if "rosters" not in st.session_state:
    st.session_state.rosters = {f"Team {i+1}": [] for i in range(NUM_TEAMS)}

# Title
st.title("🏈 Fantasy Football Auction Draft Assistant")

# Sidebar: Upload player data
st.sidebar.header("📥 Upload Player List")
uploaded_file = st.sidebar.file_uploader("Upload CSV with columns: Name, Position, Team, ProjPoints, AAV", type="csv")
if uploaded_file:
    st.session_state.players = pd.read_csv(uploaded_file)

# Main: Available players
st.header("📋 Available Players")
available_players = st.session_state.players[~st.session_state.players["Name"].isin(st.session_state.drafted["Name"])]
st.dataframe(available_players)

# Draft a player
st.subheader("🎯 Draft a Player")
with st.form("draft_form"):
    if not available_players.empty:
        player_name = st.selectbox("Select Player", available_players["Name"])
        team_owner = st.selectbox("Select Team", list(st.session_state.budgets.keys()))
        bid = st.number_input("Winning Bid ($)", min_value=1, max_value=200, step=1)
        submitted = st.form_submit_button("Draft Player")

        if submitted:
            player_row = available_players[available_players["Name"] == player_name].iloc[0]
            if bid <= st.session_state.budgets[team_owner]:
                st.session_state.budgets[team_owner] -= bid
                drafted_player = player_row.to_dict()
                drafted_player["TeamOwner"] = team_owner
                drafted_player["Bid"] = bid
                st.session_state.drafted = pd.concat([st.session_state.drafted, pd.DataFrame([drafted_player])], ignore_index=True)
                st.session_state.rosters[team_owner].append(drafted_player)
                st.success(f"{player_name} drafted by {team_owner} for ${bid}")
            else:
                st.error("Insufficient budget!")

# Team Budgets
st.subheader("💰 Team Budgets")
budget_df = pd.DataFrame(list(st.session_state.budgets.items()), columns=["Team", "Remaining Budget"])
st.dataframe(budget_df)

# Team Rosters
st.subheader("📦 Team Rosters")
selected_team = st.selectbox("View Roster for Team", list(st.session_state.rosters.keys()))
roster_df = pd.DataFrame(st.session_state.rosters[selected_team])
if not roster_df.empty:
    st.dataframe(roster_df[["Name", "Position", "Bid", "ProjPoints"]])
else:
    st.write("No players drafted yet.")
