
import streamlit as st
import pandas as pd

# Load player data
try:
    df = pd.read_csv("sample_players_with_adp.csv")
except Exception as e:
    st.error(f"Error loading player data: {e}")
    st.stop()

# Initialize session state
if "drafted_players" not in st.session_state:
    st.session_state.drafted_players = []
if "team_budgets" not in st.session_state:
    st.session_state.team_budgets = {f"Team {i+1}": {"budget": 200, "players": []} for i in range(12)}

st.title("🏈 Fantasy Football Auction Draft Assistant")

# Display available players
st.header("Available Players")
drafted_names = [p["Name"] for p in st.session_state.drafted_players]
available_players = df[~df["Name"].isin(drafted_names)]
st.dataframe(available_players.sort_values(by="ProjectedPoints", ascending=False))

# Draft a player
st.header("Draft a Player")
with st.form("draft_form"):
    player_name = st.selectbox("Select Player", available_players["Name"])
    team = st.selectbox("Select Team", list(st.session_state.team_budgets.keys()))
    bid = st.number_input("Winning Bid ($)", min_value=1, max_value=200, step=1)
    submitted = st.form_submit_button("Draft Player")

    if submitted:
        player_row = df[df["Name"] == player_name].iloc[0]
        if bid > st.session_state.team_budgets[team]["budget"]:
            st.error("Not enough budget!")
        else:
            st.session_state.drafted_players.append(player_row.to_dict())
            st.session_state.team_budgets[team]["budget"] -= bid
            st.session_state.team_budgets[team]["players"].append({**player_row.to_dict(), "Bid": bid})
            st.success(f"{player_name} drafted by {team} for ${bid}")

# Show team budgets and rosters
st.header("Team Budgets and Rosters")
for team, data in st.session_state.team_budgets.items():
    st.subheader(f"{team} - Remaining Budget: ${data['budget']}")
    if data["players"]:
        team_df = pd.DataFrame(data["players"])
        team_df["ValueScore"] = team_df["ProjectedPoints"] / team_df["Bid"]
        st.dataframe(team_df[["Name", "Position", "ProjectedPoints", "Bid", "ValueScore"]])
    else:
        st.write("No players drafted yet.")

# Tier-based draft board
st.header("Tier-Based Draft Board")
positions = df["Position"].unique()
for pos in positions:
    st.subheader(f"Top {pos}s")
    top_players = available_players[available_players["Position"] == pos].sort_values(by="ProjectedPoints", ascending=False).head(10)
    st.dataframe(top_players[["Name", "Team", "ProjectedPoints", "AAV", "ADP"]])

# Sleeper suggestions
st.header("Sleeper Suggestions")
if "ADP" in df.columns:
    sleepers = available_players.copy()
    sleepers["SleeperScore"] = sleepers["ADP"] - sleepers["ProjectedPoints"].rank(ascending=False)
    sleeper_candidates = sleepers.sort_values(by="SleeperScore", ascending=False).head(10)
    st.dataframe(sleeper_candidates[["Name", "Position", "ProjectedPoints", "ADP", "SleeperScore"]])
else:
    st.warning("ADP data not available for sleeper analysis.")
