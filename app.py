import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
# Importing the independent modules
from data_loader import load_and_prepare_data, ROLE_PLAYERS_MAP
from graphs.rankings import show_rankings
from graphs.bubble_chart import show_bubble_charts
from graphs.eff_chart import show_efficiency_chart
from graphs.early_game_chart import show_early_game_chart
from graphs.impact_chart import show_impact_chart
from graphs.misc import show_player_origin_map, show_all_rankings
from team_overview import show_overview
from pickems import show_pickems_page

load_dotenv()

def get_db_engine_():
    url = f"postgresql+psycopg2://{os.getenv('user')}:{os.getenv('password')}@{os.getenv('endpoint')}:{os.getenv('port')}/{os.getenv('dbname')}"
    engine = create_engine(url)

    with engine.connect():
        st.sidebar.success("Database connection successful!")
    return engine

@st.cache_resource
def get_db_engine():
    """
    Retrieves granular database credentials from st.secrets and
    creates a SQLAlchemy engine, caching the result.
    """
    # Define required keys for the connection string
    required_secrets = ['user', 'password', 'endpoint', 'port', 'dbname']

    #Check for missing secrets first
    for key in required_secrets:
        if key not in st.secrets:
            st.error(f"Missing required secret key: '{key}'. Please ensure it is added to your Streamlit secrets.")
            return None

    try:
        DATABASE_URL = (
            f"postgresql+psycopg2://{st.secrets.user}:{st.secrets.password}"
            f"@{st.secrets.endpoint}:{st.secrets.port}/{st.secrets.dbname}"
        )

        engine = create_engine(DATABASE_URL)

        with engine.connect():
            st.sidebar.success("Database connection successful!")
        return engine

    except Exception as e:
        # Display an error if the connection fails
        st.sidebar.error(f"DB Connection Failed: Check secrets, URL format, or firewall. Error: {e}")
        return None


# --- App Configuration ---
st.set_page_config(
    page_title="LoL Player Stats Analyzer (S15)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set global plotting style for consistency
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Inter', 'Arial']

st.markdown("""
    <style>
    /* Centers the main content block */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
        margin: auto;
        max-width: 1200px;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading data and running SQL query...")
def get_data(_engine, role: str, split: str):
    """
    Wrapper function to load data using Streamlit caching.
    This function invalidates the cache when the 'role' changes.
    """
    # Load and prepare data using the dynamic function
    return load_and_prepare_data(_engine, role, split)


def main():
    """The main function to run the Streamlit app."""

    st.title("WORLDS 2025, Player and Team Overview")
    st.image("images/worlds.png")
    st.logo("images/worlds.png", size="large")

    # --- Sidebar for Filtering ---
    st.sidebar.header("Data Source & Selection")

    # Get the Database Engine
    engine = get_db_engine()
    st.error("Cannot proceed without a successful database connection.")
    return

    # Role Selector
    role_options = list(ROLE_PLAYERS_MAP.keys())
    selected_role = st.sidebar.selectbox(
        "Select Player Role to Analyze:",
        options=role_options,
        index=5 # Default to All
    )

    # Split Selector
    split_options = ["ALL", "Spring", "Winter", "Summer", "Pre-Season"]
    selected_split = st.sidebar.selectbox(
        "Filter by Split:",
        options=split_options,
        index=0  # Default to ALL
    )

    #Load Data based on the selected role
    df_filtered = get_data(engine, selected_role, selected_split)
    df_all = get_data(engine, "All", "ALL")

    # Check if data was successfully loaded
    if df_filtered.empty or df_filtered.shape[0] == 0:
        st.warning(
            f"No data retrieved from the database for the **{selected_role}** role. Please check the DB connection and the player list in `data_loader.py`.")
        return

    # --- Sidebar for Navigation ---
    st.sidebar.markdown("---")
    st.sidebar.title("View Metrics")
    options = st.sidebar.radio("Select Analysis Type:", [
        "Team Overview",
        "Player Overview & Rankings",
        "Win/KDA & Games Analysis",
        "Economic & Efficiency Charts",
        "Early Game & Vision Control",
        "Player Origins",
        "Other charts",
        "Pickems Analysis"
    ])

    # --- Display content based on the selected section ---
    if options == "Team Overview":
        show_overview()

    elif options == "Player Overview & Rankings":
        # --- Display Player Summary ---
        st.subheader(f"Players Loaded: {selected_role} ({df_filtered.shape[0]} Found)")
        st.dataframe(df_filtered[['name', 'games', 'winrate', 'kda', 'gpm', 'kp', 'impact_score']].sort_values(by='kda',
                                                                                                               ascending=False),
                     width='stretch', hide_index=True)
        st.markdown("---")
        st.markdown("Select a role in the sidebar to load and analyze player data from the database.")
        show_rankings(df_filtered)

    elif options == "Win/KDA & Games Analysis":
        st.header("Winrate, KDA, and Games Played")
        show_bubble_charts(df_filtered, selected_role)

    elif options == "Economic & Efficiency Charts":
        st.header("Economic & Damage Efficiency")
        col1, col2 = st.columns(2)

        show_efficiency_chart(df_filtered, selected_role)  # CSM vs DPM

        show_impact_chart(df_filtered, selected_role)  # GPM vs KP

    elif options == "Early Game & Vision Control":
        st.header("Early Game Advantage & Vision Control")
        col1, col2 = st.columns(2)

        show_early_game_chart(df_filtered, selected_role)  # GD15 vs CSD15

        st.subheader("Vision Score per Minute (VSPM)")
        st.warning("Future Chart: VSPM vs KP (Vision Control)")

    elif options == "Player Origins":
        st.header("Player Origins")
        show_player_origin_map(df_all)

    elif options == "Other charts":
        st.header("Other charts")
        show_all_rankings(df_filtered)

    elif options == "Pickems Analysis":
        show_pickems_page(df_filtered, engine)

main()

