import streamlit as st
import pandas as pd
from team_overview import WORLDS_TEAMS_DATA

def get_last_n_head_to_head(df_matches: pd.DataFrame, team1: str, team2: str):
    """
    Retrieves the last N head-to-head matches played between two specified teams.

    Args:
        df_matches: DataFrame containing the match history data.
                    Expected columns include 'team1', 'team2', 'date', 'winner', 'loser'.
        team1: The name of the first team.
        team2: The name of the second team.
        n: The number of recent matches to return (default is 5).

    Returns:
        A DataFrame containing the last N head-to-head matches, sorted by date
        (most recent first), or an empty DataFrame if no matches are found.
    """
    if df_matches.empty:
        return pd.DataFrame()

    # Ensure date is in datetime format for correct sorting
    if 'date' in df_matches.columns:
        df_matches['date'] = pd.to_datetime(df_matches['date'], errors='coerce')
        df_matches['date'] = df_matches['date'].dt.date
    else:
        # Cannot sort if 'date' column is missing
        return pd.DataFrame()

    # Filter for matches where team1 and team2 participated against each other
    # Condition 1: (team1 vs team2)
    condition1 = (df_matches['team1'] == team1) & (df_matches['team2'] == team2)
    # Condition 2: (team2 vs team1)
    condition2 = (df_matches['team1'] == team2) & (df_matches['team2'] == team1)

    # Combine conditions to get all head-to-head matches
    df_h2h = df_matches[condition1 | condition2].copy()

    if df_h2h.empty:
        return pd.DataFrame()

    # Sort by date in descending order (most recent first)
    df_h2h_sorted = df_h2h.sort_values(by='date', ascending=False)

    # Return the last N matches
    return df_h2h_sorted


def compare_page(df: pd.DataFrame):

    all_teams = [
        "100 Thieves", "Anyone s Legend", "Bilibili Gaming", "CTBC Flying Oyster",
        "FlyQuest", "Fnatic", "G2 Esports", "Gen.G eSports", "Hanwha Life eSports",
        "Invictus Gaming", "KT Rolster", "Movistar KOI", "PSG Talon", "T1",
        "Team Secret Whales", "Top Esports", "Vivo Keyd Stars"
    ]
    all_teams.sort()

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        team_a = st.selectbox("Select Team A:", all_teams, index=0)
    with col_t2:
        team_b = st.selectbox("Select Team B:", all_teams, index=1)

    if team_a and team_b and team_a != team_b:
        # Get last 5 matches
        h2h_data = get_last_n_head_to_head(df, team_a, team_b)

        image_team_a = "https://placehold.co/50x50/cccccc/000000?text=LOGO"
        image_team_b = "https://placehold.co/50x50/cccccc/000000?text=LOGO"

        # Iterate through the nested dictionary to find the logo for both teams
        for league_data in WORLDS_TEAMS_DATA.values():
            for team in league_data.get("teams", []):
                if team["name"] == team_a:
                    image_team_a = team["logo"]
                if team["name"] == team_b:
                    image_team_b = team["logo"]

        if not h2h_data.empty:
            # Prepare a display table with only the most relevant columns
            ind_game_wins_a = 0
            ind_game_wins_b = 0

            # Iterate through the matches to aggregate individual game scores
            for _, row in h2h_data.iterrows():
                # Case 1: Team A is team1 in the match
                if row['team1'] == team_a:
                    ind_game_wins_a += row['team1_score']
                    ind_game_wins_b += row['team2_score']
                # Case 2: Team A is team2 in the match (the only other possibility)
                elif row['team2'] == team_a:
                    ind_game_wins_a += row['team2_score']
                    ind_game_wins_b += row['team1_score']

                if row['team1'] == team_a:
                    score_a = row['team1_score']
                    score_b = row['team2_score']
                else:  # Assumes row['team2'] == team_a
                    score_a = row['team2_score']
                    score_b = row['team1_score']

                score  = f"{team_a} {score_a} - {score_b} {team_b}"

                h2h_data['H2H Score'] = score

            # Simple H2H record summary
            wins_a = (h2h_data['winner'] == team_a).sum()
            wins_b = (h2h_data['winner'] == team_b).sum()

            st.markdown(f"**Head-to-Head Record (Last {len(h2h_data)} Games):**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(image_team_a, width=100)
                st.subheader(team_a)
                st.metric(label='Series (Games)', value=f"{wins_a}({ind_game_wins_a})")
            with col2:
                st.markdown("",unsafe_allow_html=True)
                st.markdown("<h2 style='text-align: center;'>WINS</h2>", unsafe_allow_html=True)
                st.markdown("<h2 style='text-align: center;'>--</h2>", unsafe_allow_html=True)
            with col3:
                st.image(image_team_b, width=100)
                st.subheader(team_b)
                st.metric(label='Series (Games)', value=f"{wins_b}({ind_game_wins_b})")

            display_cols = ['date', 'tournament_name', 'H2H Score', 'match_type']
            st.table(h2h_data[display_cols].rename(columns={
                'tournament_name': 'Tournament',
                'match_type': 'Type'
            }))

        else:
            st.info(f"No match history found between {team_a} and {team_b} in the current dataset.")

    elif team_a == team_b:
        st.warning("Please select two different teams to compare.")
    else:
        st.info("Please select two teams for comparison.")