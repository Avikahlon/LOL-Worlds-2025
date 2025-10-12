import pandas as pd
from sqlalchemy.engine import Engine
from typing import List, Dict
import streamlit as st

ROLE_PLAYERS_MAP: Dict[str, List[str]] = {
    "Mid": ['Faker', 'Chovy', 'Zeka', 'Bdd', 'Knight', 'Shanks', 'Creme', 'RooKie', 'Poby', 'Caps', 'jojopyun', 'Quad', 'Mireu', 'Quid', 'HongQ', 'Maple', 'Dire'],
    "Jungle": ['Oner', 'Canyon', 'Peanut', 'Cuzz', 'Beichuan', 'Shad0w', 'Tarzan', 'Kanavi', 'Wei', 'Inspired', 'Disamis', 'River', 'SkewMond', 'Razork', 'Elyoya', 'JunJia', 'Hizto', 'Karsa'],
    "Top": ['Doran', 'Kiin', 'PerfecT', 'Zeus', 'TheShy', 'Bin', 'Flandre', '369', 'Brokenblade', 'Oscarinin', 'Myrwn', 'Gakgos', 'Bwipo', 'Boal', 'Dhokla', 'Driver', 'Rest', 'Hiro02', 'Pun', 'Azhi'],
    "ADC": ['Ruler', 'Gumayusi', 'Viper', 'deokdam', 'Elk', 'Hope', 'JackeyLove', 'GALA', 'Massu', 'FBI', 'Morttheus', 'Upset', 'Hans Sama', 'Supa', 'Doggo', 'Eddie', 'Betty'],
    "Support": ['Keria', 'Delight', 'Duro', 'Peter', 'ON', 'Kael', 'Hang', 'Meiko', 'Busio', 'Trymbi', 'Eyla', 'Labrov', 'Alvaro', 'Mikyx', 'Kaiwing', 'Taki', 'Woody'],
    "All": [
        'Faker', 'Chovy', 'Zeka', 'Bdd', 'Knight', 'Shanks', 'Creme', 'RooKie', 'Poby', 'Caps', 'jojopyun', 'Quad', 'Mireu', 'Quid', 'HongQ', 'Maple', 'Dire',
        'Oner', 'Canyon', 'Peanut', 'Cuzz', 'Beichuan', 'Shad0w', 'Tarzan', 'Kanavi', 'Wei', 'Inspired', 'Disamis', 'River', 'SkewMond', 'Razork', 'Elyoya', 'JunJia', 'Hizto', 'Karsa',
        'Doran', 'Kiin', 'PerfecT', 'Zeus', 'TheShy', 'Bin', 'Flandre', '369', 'Brokenblade', 'Oscarinin', 'Myrwn', 'Gakgos', 'Bwipo', 'Boal', 'Dhokla', 'Driver', 'Rest', 'Hiro02', 'Pun', 'Azhi',
        'Ruler', 'Gumayusi', 'Viper', 'deokdam', 'Elk', 'Hope', 'JackeyLove', 'GALA', 'Massu', 'FBI', 'Morttheus', 'Upset', 'Hans Sama', 'Supa', 'Doggo', 'Eddie', 'Betty',
        'Keria', 'Delight', 'Duro', 'Peter', 'ON', 'Kael', 'Hang', 'Busio', 'Trymbi', 'Eyla', 'Labrov', 'Alvaro', 'Mikyx', 'Kaiwing', 'Taki', 'Woody'
    ],
}

TEAM_MAP = [
        'Gen.G eSports', 'T1', 'KT Rolster', 'Hanwha Life eSports',
        'Bilibili Gaming', 'Top Esports', 'Anyone s Legend', 'Invictus Gaming',
        'G2 Esports', 'Fnatic', 'Movistar KOI', '100 Thieves', 'FlyQuest',
        'Vivo Keyd Stars', 'Team Secret Whales', 'CTBC Flying Oyster', 'PSG Talon'
]

# @st.cache_data
def load_team_map():
    """Loads and caches the player-team-league mapping from player_team_map.csv."""
    try:
        df_map = pd.read_csv("player_team_names.csv")
        # Ensure the essential columns exist
        if 'name' not in df_map.columns or 'team' not in df_map.columns or 'league' not in df_map.columns:
            st.error("player_team_names.csv must contain 'name', 'team', and 'league' columns.")
            return pd.DataFrame({'name': [], 'team': [], 'league': []})

        return df_map[['name', 'team', 'league']]
    except FileNotFoundError:
        st.error("player_team_names not found! Please create this file with player, team, and league data.")
        return pd.DataFrame({'name': [], 'team': [], 'league': []})
    except Exception as e:
        st.error(f"Error loading player_team_map.csv: {e}")
        return pd.DataFrame({'name': [], 'team': [], 'league': []})

def load_team_data(engine: Engine, selected_split: str):
    """
        Fetches aggregated team stats from the 'teams_staging' table,
        filtering for teams present in the loaded player map.

        This function leverages st.cache_data to only query the database once.
        """
    # 1. Get the DataFrame containing player/team/league mapping
    teams = TEAM_MAP

    # 2. Extract unique team names from the map


    if not teams:
        st.error("No teams found in the player map. Cannot load team data.")
        return pd.DataFrame()

    # 3. Format the list for the SQL IN clause
    teams_list_str = ', '.join([f"'{team}'" for team in teams])

    # 4. Construct the SQL statement
    target_season = 'S15'
    statement = f"""
            SELECT * FROM teams_staging
            WHERE name IN ({teams_list_str})
            AND season = '{target_season}'
            AND split = '{selected_split}';
        """

    # 5. Execute the query and load into DataFrame
    try:
        team_df = pd.read_sql(statement, engine)

        # Simple cleaning and return
        team_df = team_df.fillna(0)  # Fill NaN for numeric stats
        return team_df

    except Exception as e:
        st.error(f"Error executing SQL query for team data: {e}")
        return pd.DataFrame()

def load_and_prepare_data(engine: Engine, selected_role: str, selected_split: str):
    """
    Fetches player stats from the 'players_staging' table for a specific season
    and role, then cleans and prepares the data for visualization.

    Args:
        engine: The SQLAlchemy Engine/Connection object for database interaction.
        selected_role: The role selected by the user (e.g., 'Mid', 'Jungle', 'All').

    Returns:
        A cleaned Pandas DataFrame ready for charting.
    """

    player_names = ROLE_PLAYERS_MAP.get(selected_role, [])

    if not player_names:
        print(f"Error: No players found for role '{selected_role}'. Returning empty DataFrame.")
        # Return empty DataFrame with necessary columns to prevent downstream errors
        expected_cols = ['name', 'country', 'games', 'winrate', 'kda', 'gpm', 'kp', 'csm', 'dpm', 'gd15', 'csd15', 'vspm',
                         'impact_score']
        return pd.DataFrame(columns=expected_cols)

    names_list_str = ', '.join([f"'{name}'" for name in player_names])

    target_season = 'S15'
    player_statement = f"""
        SELECT * FROM players_staging
        WHERE season = '{target_season}'
        AND name IN ({names_list_str})  
        AND split = '{selected_split}';
    """

    try:
        player_df = pd.read_sql(player_statement, engine)
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        # Fallback in case of DB connection or SQL execution failure
        expected_cols = ['name', 'games', 'winrate', 'kda', 'avg_kills', 'avg_deaths', 'avg_assists', 'gpm', 'kp',
                         'csm', 'dpm', 'gd15', 'csd15', 'xpd15', 'vspm', 'solo_kills',
                         'impact_score', 'team', 'league']
        return pd.DataFrame(columns=expected_cols)

    #Check for Missing Players ---
    fetched_names = set(player_df['name'])
    missing_names = [name for name in player_names if name not in fetched_names]

    if missing_names:
        st.warning(
            f"⚠️ **Data Warning:** {len(missing_names)} player(s) were requested for '{selected_role}' but not found in the database "
            f"for season '{target_season}' and split '{selected_split}'. "
            f"Missing: {', '.join(missing_names[:5])}{'...' if len(missing_names) > 5 else ''}"
        )

    # --- Data Cleaning and Metric Calculation ---

    # Define all numeric columns
    numeric_cols = ['games', 'winrate', 'kda', 'avg_kills', 'avg_deaths', 'avg_assists', 'gpm', 'kp', 'csm', 'dpm',
                    'gd15', 'csd15', 'xpd15', 'vspm', 'solo_kills']

    # Convert columns to numeric, coercing errors (NaNs)
    for col in numeric_cols:
        player_df[col] = pd.to_numeric(player_df[col], errors='coerce')

    #Filter out players with insufficient games (essential filter)
    df_cleaned = player_df[player_df['games'] >= 10].copy()

    # FILL NaNs with 0 instead of dropping rows to keep all players with a sufficient game count.
    df_cleaned = df_cleaned.copy()
    df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(0)

    # Metric Calculation (Impact Score)
    # Scaling KP (0-1) by 500 makes it comparable to GPM (400-500 range)
    df_cleaned['impact_score'] = (df_cleaned['gpm'] * 0.5) + (df_cleaned['kp'] / 100 * 0.5 * 500)

    #Load Team Map and Merge
    df_team_map = load_team_map()

    # Merge on the player name
    df_cleaned = df_cleaned.merge(
        df_team_map,
        on='name',
        how='left'
    )

    # Fill missing team info (for players not in your CSV map)
    df_cleaned['team_name'] = df_cleaned['team'].fillna('Free Agent')
    df_cleaned['league'] = df_cleaned['league'].fillna('Unknown League')

    # Ensure consistent column naming (using 'team_name' as per other files)
    if 'team_name' not in df_cleaned.columns:
        df_cleaned = df_cleaned.rename(columns={'team': 'team_name'})

    if 'team' in df_cleaned.columns:
        df_cleaned = df_cleaned.drop(columns=['team'])

    return df_cleaned


def load_match_data(engine):

    names_list_str = ', '.join([f"'{name}'" for name in TEAM_MAP])

    statement = f"""
        SELECT * FROM matches_staging
        WHERE winner IN ({names_list_str})
        OR winner IN ({names_list_str});
    """

    try:
        matches_df = pd.read_sql(statement, engine)
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return pd.DataFrame()

    return matches_df