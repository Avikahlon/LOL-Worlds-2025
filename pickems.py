import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.engine import Engine

WORLDS_PLAYER_LIST = [
    'Faker', 'Chovy', 'Zeka', 'Bdd', 'Knight', 'Shanks', 'Creme', 'RooKie', 'Poby', 'Caps',
    'jojopyun', 'Quad', 'Mireu', 'Quid', 'HongQ', 'Maple', 'Dire', 'Oner', 'Canyon', 'Peanut',
    'Cuzz', 'Beichuan', 'Shadow', 'Tarzan', 'Kanavi', 'Wei', 'Inspired', 'Disamis', 'River',
    'Skewmond', 'Razork', 'Elyoya', 'JunJia', 'Hizto', 'Karsa', 'Doran', 'Kiin', 'PerfecT',
    'Zeus', 'TheShy', 'Bin', 'Flandre', '369', 'BrokenBlade', 'Oscarinin', 'Myrwn', 'Gakgos',
    'Bwipo', 'Boal', 'Dhokla', 'Driver', 'Rest', 'Hiro02', 'Pun', 'Azhi', 'Ruler', 'Gumayusi',
    'Viper', 'deokdam', 'Elk', 'Hope', 'JackeyLove', 'GALA', 'Massu', 'FBI', 'Morttheus',
    'Upset', 'Hans Sama', 'Supa', 'Doggo', 'Eddie', 'Betty', 'Keria', 'Delight', 'Duro',
    'Peter', 'ON', 'Kael', 'Hang', 'Busio', 'Trymbi', 'Eyla', 'Labrov', 'Alvaro', 'MikyX',
    'Kaiwing', 'Taki', 'Woody'
]

WORLDS_TEAM_LIST = [
    'Gen.G eSports', 'T1', 'KT Rolster', 'Hanwha Life eSports',
    'Bilibili Gaming', 'Top Esports', 'Anyone s Legend', 'Invictus Gaming',
    'G2 Esports', 'Fnatic', 'Movistar KOI', '100 Thieves', 'FlyQuest',
    'Vivo Keyd Stars', 'Team Secret Whales', 'CTBC Flying Oysters', 'PSG Talon'
]


@st.cache_data
def _load_team_data(_engine: Engine) -> pd.DataFrame:
    """Loads team data (game duration and average kills) from the database."""
    team_list_str = "', '".join(WORLDS_TEAM_LIST)

    try:
        # Query 1: Average Game Duration and Region
        query_duration = f"""
        SELECT 
            name, 
            region,
            AVG(game_duration) AS average_game_duration
        FROM 
            teams_staging
        WHERE 
            season = 'S15' 
            AND name IN ('{team_list_str}')
        GROUP BY 
            name, region;
        """
        df_duration = pd.read_sql(query_duration, _engine)

        # Query 2: Average Kills Per Game
        query_kills = f"""
        SELECT 
            name, 
            AVG(kills_per_game) AS average_kills_per_game 
        FROM 
            teams_staging
        WHERE 
            season = 'S15' 
            AND name IN ('{team_list_str}')
        GROUP BY 
            name;
        """
        df_kills = pd.read_sql(query_kills, _engine)

        # Merge the two dataframes on team name
        team_data = pd.merge(df_duration, df_kills, on='name', how='inner')
        return team_data

    except Exception as e:
        st.error(f"Error loading team data from database: {e}")
        # Return an empty DataFrame on error
        return pd.DataFrame({'name': [], 'region': [], 'average_game_duration': [], 'average_kills_per_game': []})


def _filter_and_display_top_players(df: pd.DataFrame, column: str, title: str, ascending: bool = False,
                                    top_n: int = 10):
    """Filters player DataFrame, displays top results, and generates a simple bar chart."""

    #Filter the raw data to include only players in the pickems list
    df_pickems = df[df['name'].isin(WORLDS_PLAYER_LIST)].copy()

    #Sort and select top N
    df_top = df_pickems.sort_values(by=column, ascending=ascending).head(top_n)

    st.subheader(f"📊 {title}")

    # Display table
    st.dataframe(
        df_top[['name', 'team_name', 'league', column, 'games']].rename(
            columns={column: title.split('(')[0].strip(), 'team': 'Team', 'league': 'League', 'games': 'Games'}
        ).set_index('name')
    )

    # Display chart
    fig = px.bar(
        df_top,
        x='name',
        y=column,
        color='team_name',
        title=f'Top {top_n} Players by {title.split("(")[0].strip()}',
        hover_data=['team_name', 'league', 'games'],
        labels={'name': 'Player Name', column: title.split('(')[0].strip()}
    )
    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig)


def show_pickems_page(df_players: pd.DataFrame, engine: Engine):
    """Renders the Pickems Analysis page with data-driven insights."""

    st.title("🏆 Worlds 2025 Pickems Analysis")
    st.markdown(
        """
        This page summarizes the core statistical queries used to inform the final **Worlds Pickems** decisions. 
        It prioritizes players and teams with high-impact, aggressive metrics.
        """
    )

    st.markdown("---")

    #Player-Focused Aggression & Efficiency
    st.header("Player Analysis: Aggression and Consistency")

    # Most First Bloods (FB%)
    _filter_and_display_top_players(
        df_players,
        column='fb_pct',
        title='First Blood Percentage (FB%)',
        top_n=8
    )

    st.markdown("---")

    # Best KDA
    _filter_and_display_top_players(
        df_players,
        column='kda',
        title='Kill-Death-Assist Ratio (KDA)',
        top_n=8
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # Average Kills
        _filter_and_display_top_players(
            df_players,
            column='avg_kills',
            title='Average Kills Per Game',
            top_n=5
        )

    with col2:
        # Penta Kills
        df_penta = df_players[df_players['name'].isin(WORLDS_PLAYER_LIST)].copy()
        df_penta = df_penta[df_penta['penta_kills'] > 0]

        st.subheader("📊 Penta Kills")
        if df_penta.empty:
            st.info("No players in the selected list have recorded a Penta Kill.")
        else:
            df_top_penta = df_penta.sort_values(by='penta_kills', ascending=False)[['name', 'team_name', 'penta_kills']]
            st.dataframe(
                df_top_penta.rename(columns={'team': 'Team', 'penta_kills': 'Pentas'}).set_index('name')
            )

    st.markdown("---")

    #Team-Focused Metrics
    st.header("Team Analysis: Tempo and Playstyle")

    #Load team data from the database
    team_data = _load_team_data(engine)

    col_kills, col_duration = st.columns(2)

    if not team_data.empty:
        with col_kills:
            # Most Team Kills
            st.subheader("📈 Average Kills Per Game (Team)")
            df_kills = team_data.sort_values(by='average_kills_per_game', ascending=False).head(10)

            fig_kills = px.bar(
                df_kills,
                x='name',
                y='average_kills_per_game',
                color='region',
                title='Top Teams by Kills Per Game',
                labels={'average_kills_per_game': 'Kills Per Game', 'name': 'Team'}
            )
            fig_kills.update_layout(xaxis={'categoryorder': 'total descending'})
            st.plotly_chart(fig_kills)

        with col_duration:
            # Average Game Time
            st.subheader("⏱️ Average Game Duration (Team)")
            df_duration = team_data.sort_values(by='average_game_duration', ascending=True).head(10)

            fig_duration = px.bar(
                df_duration,
                x='name',
                y='average_game_duration',
                color='region',
                title='Fastest Game Duration (Lower is faster)',
                labels={'average_game_duration': 'Game Duration (Seconds)', 'name': 'Team'}
            )
            fig_duration.update_layout(xaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_duration)
    else:
        st.warning("Team data could not be loaded from the database. Displaying player analysis only.")
    st.markdown("---")

    #Pickems Final Decision
    st.header("Final Pickems Decision")

    st.markdown("""
        ### Analysis Summary: Data, Bias, and Regional Nuance
        
        My pickems were fundamentally inspired by the data, historical context, and high-stakes plays, but my **personal bias** and **regional expertise** played a crucial role in the final choices.
        
        The raw numbers (like high **KDA** and **FB%**) set the foundation, pointing towards statistically dominant teams. However, my understanding of the **regional differences**—nuances in playstyle, meta adaptation, and international pressure that the seasonal data might not fully convey—guided the tie-breaking decisions. This included a degree of bias towards certain favorite players and teams known for performing under pressure, elevating them above a purely statistical ranking.
        
        Ultimately, the final selections are a blend of objective analysis, trust in historical performance, and subjective judgment of which teams are best equipped to navigate the complex challenges of a world championship.
        """
    )

    st.subheader("My Pickems Screenshot")
    st.image("images/pickems.png")

    st.markdown("---")