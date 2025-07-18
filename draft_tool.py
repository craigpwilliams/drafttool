
import streamlit as st
import pandas as pd

# Load player data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("sample_players.csv")
        if 'Name' not in df.columns or 'Position' not in df.columns or 'ProjectedPoints' not in df.columns or 'AAV' not in df.columns:
            st.error("CSV file must contain 'Name', 'Position', 'ProjectedPoints', and 'AAV' columns.")
            return pd.DataFrame()
        df['ValueScore'] = df['ProjectedPoints'] / df['AAV']
        if 'ADP' not in df.columns:
            df['ADP'] = None
        return df
    except Exception as e:
        st.error(f"Error loading player data: {e}")
        return pd.DataFrame()

# Initialize session state
def init_session_state(teams):
    if "drafted_players" not in st.session_state:
        st.session_state.drafted_players = []
    if "team_rosters" not in st.session_state:
        st.session_state.team_rosters = {team: [] for team in teams}
    if "team_budgets" not in st.session_state:
        st.session_state.team_budgets = {team: 200 for team in teams}

# Draft a player
def draft_player(player_name, team, bid):
    player_row = df[df['Name'] == player_name]
    if not player_row.empty:
        player_data = player_row.iloc[0].to_dict()
        player_data.update({"Team": team, "Bid": bid})
        st.session_state.drafted_players.append(player_data)
        st.session_state.team_rosters[team].append(player_data)
        st.session_state.team_budgets[team] -= bid

# Display team rosters
def display_rosters():
    st.subheader("Team Rosters")
    for team, players in st.session_state.team_rosters.items():
        st.markdown(f"**{team}** - Budget Left: ${st.session_state.team_budgets[team]}")
        if players:
            df_team = pd.DataFrame(players)
            st.dataframe(df_team[['Name', 'Position', 'Bid', 'ProjectedPoints']])
        else:
            st.write("No players drafted yet.")

# Display tier-based draft board
def display_tiers(df):
    st.subheader("Tier-Based Draft Board")
    for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
        st.markdown(f"**Top {pos}s**")
        top_players = df[(df['Position'] == pos) & (~df['Name'].isin([p['Name'] for p in st.session_state.drafted_players]))]
        st.dataframe(top_players.sort_values(by='ProjectedPoints', ascending=False).head(10)[['Name', 'Team', 'ProjectedPoints', 'AAV', 'ValueScore']])

# Display value picks
def display_value_picks(df):
    st.subheader("Top Value Picks")
    available = df[~df['Name'].isin([p['Name'] for p in st.session_state.drafted_players])]
    st.dataframe(available.sort_values(by='ValueScore', ascending=False).head(10)[['Name', 'Position', 'ProjectedPoints', 'AAV', 'ValueScore']])

# Display sleeper suggestions
def display_sleepers(df):
    st.subheader("Sleeper Suggestions")
    if df['ADP'].isnull().all():
        st.info("No ADP data available to calculate sleepers.")
        return
    df = df.dropna(subset=['ADP'])
    df['SleeperScore'] = df['ProjectedPoints'] / df['ADP']
    sleepers = df[~df['Name'].isin([p['Name'] for p in st.session_state.drafted_players])]
    st.dataframe(sleepers.sort_values(by='SleeperScore', ascending=False).head(10)[['Name', 'Position', 'ProjectedPoints', 'ADP', 'SleeperScore']])

# Display budget strategy
def display_budget_strategy():
    st.subheader("Budget Strategy")
    ideal_spend = {
        'QB': 20, 'RB': 60, 'WR': 60, 'TE': 15, 'FLEX': 25, 'K': 5, 'DEF': 5, 'BENCH': 10
    }
    st.write("Ideal Spend by Position (example):")
    st.json(ideal_spend)

    actual_spend = {}
    for team, players in st.session_state.team_rosters.items():
        spend_by_pos = {}
        for p in players:
            pos = p['Position']
            spend_by_pos[pos] = spend_by_pos.get(pos, 0) + p['Bid']
        actual_spend[team] = spend_by_pos

    for team, spend in actual_spend.items():
        st.markdown(f"**{team}**")
        st.json(spend)

# Display opponent budgets
def display_opponent_budgets():
    st.subheader("Opponent Budgets")
    df_budget = pd.DataFrame([
        {"Team": team, "Budget Left": budget, "Players Drafted": len(st.session_state.team_rosters[team])}
        for team, budget in st.session_state.team_budgets.items()
    ])
    st.dataframe(df_budget)

# Streamlit UI
st.title("Fantasy Football Auction Draft Assistant")

df = load_data()
teams = [f"Team {i+1}" for i in range(12)]
init_session_state(teams)

st.sidebar.header("Draft a Player")
with st.sidebar.form("draft_form"):
    player_name = st.selectbox("Select Player", df[~df['Name'].isin([p['Name'] for p in st.session_state.drafted_players])]['Name'])
    team = st.selectbox("Select Team", teams)
    bid = st.number_input("Winning Bid ($)", min_value=1, max_value=200, value=1)
    submitted = st.form_submit_button("Draft Player")
    if submitted:
        draft_player(player_name, team, bid)
        st.success(f"{player_name} drafted by {team} for ${bid}")

display_rosters()
display_tiers(df)
display_value_picks(df)
display_sleepers(df)
display_budget_strategy()
display_opponent_budgets()
