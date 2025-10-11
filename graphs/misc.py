import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_player_origin_map(df: pd.DataFrame):
    """
    Generates a global Choropleth map showing the number of participating players
    from each country based on the 'country' column (ISO-2 code) in the player data.
    """

    st.subheader("🌎 Player Origin Map: Countries Represented at Worlds")

    if df.empty or 'country' not in df.columns:
        st.info(
            "No player data available or the 'country' column is missing. Ensure your data loader returns the 'country' column.")
        return

    #ISO Alpha-2 to ISO Alpha-3 Mapping
    iso_2_to_3 = {
        "AR": "ARG", "AU": "AUS", "BE": "BEL", "BR": "BRA", "CA": "CAN",
        "CN": "CHN", "DE": "DEU", "DK": "DNK", "ES": "ESP", "FR": "FRA",
        "GR": "GRC", "HK": "HKG", "KR": "KOR", "PL": "POL", "TR": "TUR",
        "TW": "TWN", "US": "USA", "VN": "VNM"
    }

    # Create a new column with ISO-3 codes
    # Use .str.upper() just in case the codes are lowercase in the DB
    df['iso_alpha_3'] = df['country'].str.upper().map(iso_2_to_3)

    # 2. Aggregate data: Count players per country using the new ISO-3 code
    df_country = df.groupby(['country', 'iso_alpha_3']).size().reset_index(name='Player Count')

    # Filter out rows where mapping failed (iso_alpha_3 is NaN)
    df_country = df_country.dropna(subset=['iso_alpha_3'])

    if df_country.empty:
        st.info("No valid country data available for mapping.")
        return

    # 3. Create the Choropleth Map
    fig =  px.choropleth(
        df_country,
        locations='iso_alpha_3',
        locationmode='ISO-3',
        color='Player Count',
        hover_name='country',
        hover_data={'iso_alpha_3': False, 'Player Count': True},
        color_continuous_scale=px.colors.sequential.Plasma,
        projection='natural earth',
        title='Distribution of Players by Country of Origin',
        scope='world'
    )


    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=600
    )

    # 4. Display the chart
    st.plotly_chart(fig, use_container_width=True)

def _create_misc_bar_chart(df, x_col, y_col='name', color_col='league', title=None, x_label=None, grouping_var=None):
    """
    Helper function to create a standardized Plotly horizontal bar chart for player ranking.
    It sorts the DataFrame by the metric and limits results to the top 20.
    """

    # Sort the data by the ranking metric (x_col) in descending order and limit to top 20
    df_sorted = df.sort_values(by=x_col, ascending=False).head(20).copy()

    # Filter out rows where the ranking column is 0 or NaN, if the total sum is not zero
    if df_sorted[x_col].sum() > 0:
        df_sorted = df_sorted[df_sorted[x_col] > 0]

    if df_sorted.empty:
        return None

    hover_cols = ['name', 'team_name', 'league', 'games', x_col]

    fig = px.bar(
        df_sorted,
        x=x_col,
        y=y_col,
        color=color_col,
        orientation='h',
        hover_data=hover_cols,
        title=title or f'Top 20 Players by {x_col.replace("_", " ").title()}'
    )

    fig.update_layout(
        xaxis_title=x_label or x_col.replace('_', ' ').title(),
        yaxis_title='Player Name',
        height=600,
        margin=dict(l=20, r=20, t=60, b=20),
        # Ensures the largest value is at the top of the horizontal bar chart
        yaxis={'categoryorder': 'total ascending'}
    )

    return fig


# --- Individual Ranking Charts ---

def show_solo_kills_ranking(df: pd.DataFrame):
    """Ranks players by total solo kills."""
    st.caption("🔪 Solo Kill King: Most Solo Kills")

    if 'solo_kills' not in df.columns:
        st.info("The 'solo_kills' column is missing from the data.")
        return

    fig = _create_misc_bar_chart(
        df,
        x_col='solo_kills',
        title='Player Ranking by Total Solo Kills',
        x_label='Total Solo Kills',
        grouping_var='league'
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No players found with solo kills in the filtered data.")


def show_average_kills_ranking(df: pd.DataFrame):
    """Ranks players by average kills per game."""
    st.caption("💀 Highest Kills Per Game")

    if 'avg_kills' not in df.columns:
        st.info("The 'avg_kills' column is missing from the data.")
        return

    fig = _create_misc_bar_chart(
        df,
        x_col='avg_kills',
        title='Player Ranking by Average Kills Per Game',
        x_label='Average Kills (per game)',
        grouping_var='league'
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No players found with kill data in the filtered data.")


def show_average_assists_ranking(df: pd.DataFrame):
    """Ranks players by average assists per game."""
    st.caption("🤝 Highest Assists Per Game")

    if 'avg_assists' not in df.columns:
        st.info("The 'avg_assists' column is missing from the data.")
        return

    fig = _create_misc_bar_chart(
        df,
        x_col='avg_assists',
        title='Player Ranking by Average Assists Per Game',
        x_label='Average Assists (per game)',
        grouping_var='league'
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No players found with assist data in the filtered data.")


def show_damage_share_ranking(df: pd.DataFrame):
    """Ranks players by damage share percentage (dmg_pct)."""
    st.caption("🔥 Highest Damage Share Percentage")

    if 'dmg_pct' not in df.columns:
        st.info("The 'dmg_pct' column is missing from the data.")
        return

    fig = _create_misc_bar_chart(
        df,
        x_col='dmg_pct',
        title='Player Ranking by Team Damage Share %',
        x_label='Team Damage Share (%)',
        grouping_var='league'
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No players found with damage share data in the filtered data.")


def show_vision_ranking(df: pd.DataFrame):
    """Ranks players by Wards Per Minute (WPM)."""
    st.caption("👁️ Vision Score Leader (WPM)")

    if 'wpm' not in df.columns:
        st.info("The 'wpm' column is missing from the data.")
        return

    fig = _create_misc_bar_chart(
        df,
        x_col='wpm',
        title='Player Ranking by Wards Per Minute (WPM)',
        x_label='Wards Per Minute',
        grouping_var='league'
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No players found with ward data in the filtered data.")


def show_penta_kills_ranking(df: pd.DataFrame):
    """Ranks players by total penta kills."""
    st.caption("⭐️ Total Penta Kills")

    if 'penta_kills' not in df.columns:
        st.info("The 'penta_kills' column is missing from the data.")
        return

    fig = _create_misc_bar_chart(
        df,
        x_col='penta_kills',
        title='Player Ranking by Total Penta Kills',
        x_label='Total Penta Kills',
        grouping_var='league'
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No players found with Penta Kills in the filtered data.")


# --- Main Wrapper Function ---

def show_all_rankings(df: pd.DataFrame):
    """Displays all ranking charts in sequence, arranged in columns."""

    st.title("🏆 Player Ranking Leaderboards")
    st.markdown("---")

    # We will display these in separate Streamlit columns for a compact view.
    col1, col2 = st.columns(2)

    with col1:
        # Kills and Solo Kills
        show_average_kills_ranking(df)
        st.markdown("---")
        show_solo_kills_ranking(df)
        st.markdown("---")
        show_damage_share_ranking(df)

    with col2:
        # Assists and Misc Stats
        show_average_assists_ranking(df)
        st.markdown("---")
        show_vision_ranking(df)
        st.markdown("---")
        show_penta_kills_ranking(df)
