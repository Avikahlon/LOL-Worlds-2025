import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

REGION_MAP = {
    "Custom Selection": None, # Default option to enable manual multiselect
    "All Teams": None, # Will select all teams available
    "China (LPL)": ["LPL"],
    "Korea (LCK)": ["LCK"],
    "Europe (LEC)": ["LEC"],
    # Grouping NA and LAT into Americas
    "Americas": ["LTA"],
    # Grouping Taiwan and Vietnam into Asia Pacific
    "Asia Pacific": ["LCP"]
}

REGION_OPTIONS = list(REGION_MAP.keys())

def plot_single_bubble_chart(df: pd.DataFrame, x: str, y: str, size: str, title: str, xlabel: str, ylabel: str):
    """Helper function to plot a single bubble chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    fig = px.scatter(
        df, x=x, y=y, color='name', size=size, hover_data=y,
    )
    ax.set_title(title, fontsize=16)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    st.plotly_chart(fig)


def show_bubble_charts(df: pd.DataFrame, selected_role: str):

    """Displays three bubble charts: Winrate vs KDA, Winrate vs Games, KDA vs Games."""

    if selected_role.upper() == 'ALL':
        color_variable = 'team_name'
        legend_title = 'Team'
        title_group = 'Team'
    else:
        color_variable = 'league'
        legend_title = 'League'
        title_group = 'League'

    st.subheader(f"Filter by {legend_title}")

    # 1. Get all unique groups (Teams or Leagues) present in the data
    all_groups = df[color_variable].unique().tolist()
    all_groups.sort()  # Sort alphabetically for clean display

    group_filter = st.selectbox(
        "Compare teams by grouping:",
        options=REGION_OPTIONS,
        index=0  # Default to Custom Selection
    )

    all_players = df['name'].unique().tolist()
    data_to_show = []

    if group_filter == "Custom Selection":
        is_multiselect_disabled = False

        selected_groups = st.multiselect(
            label=f"Select specific {legend_title}s to display:",
            options=all_groups,
            default=all_groups  # Default to selecting all groups
        )

        data_to_show = selected_groups

        if not selected_groups:
            st.warning(f"Please select at least one {legend_title} to display the charts.")
            return  # Stop execution if no groups are selected

    else:
        is_multiselect_disabled = True
        st.caption("AA")

        region_codes = REGION_MAP[group_filter]

        if region_codes is None or group_filter == "All Teams":
            # Show ALL available teams
            data_to_show = all_players
        else:
            # Filter by the specified list of region codes (requires 'league' column)
            if 'league' in df.columns:
                # UPDATED: Use isin() to filter by the list of region codes
                data_to_show = df[df ['league'].isin(region_codes)]['name'].unique().tolist()
            else:
                st.error(
                    f"Error: Cannot filter by region '{group_filter}'. 'league' column is missing from team data. The codes expected were: {region_codes}")
                return

    if len(data_to_show) < 1:
        st.warning(f"No teams selected or found for the current filter: **{group_filter}**.")
        return

    # Filter the DataFrame using the determined list of teams
    df_filtered = df[df['name'].isin(data_to_show)].copy()

    # Check if data exists after filtering
    if df_filtered.empty:
        st.warning("No players match the current filters.")
        return

    n_groups = df_filtered[color_variable].nunique()

    st.subheader(f"KDA vs. Winrate & Games Played (Grouped by {title_group})")
    # --- 1. KDA vs Winrate Bubble Chart ---
    col1, col2 = st.columns(2)

    fig1 = px.scatter(
        df_filtered,
        x='kda',
        y='winrate',
        size='games',
        color=color_variable,  # Dynamically colored by Team or League
        hover_name='name',
        hover_data=['team_name'],# Show player name on hover
        size_max=45,  # Max size for bubbles
        opacity=0.8,
        title=f'KDA vs. Winrate (N={n_groups} {title_group}s), Size = Games Played'
    )

    # Update layout for clearer axis labels
    fig1.update_layout(
        xaxis_title='KDA (Kills + Assists) / Deaths',
        yaxis_title='Winrate (%)',
        legend_title=legend_title,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- 2. Winrate vs Games Played Bubble Chart ---
    fig2 = px.scatter(
        df_filtered,
        x='games',
        y='winrate',
        size='kda',
        color=color_variable,  # Dynamically colored by Team or League
        hover_name='name',
        size_max=45,
        opacity=0.8,
        title=f'Winrate vs. Games Played (Color = {legend_title}, Size = KDA)'
    )

    fig2.update_layout(
        xaxis_title='Games Played',
        yaxis_title='Winrate (%)',
        legend_title=legend_title,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig2, use_container_width=True)

    # --- 3. KDA vs Games Played Bubble Chart ---
    st.subheader(f"KDA vs. Games Played (Grouped by {title_group}, Bubble Size = Winrate)")
    fig3 = px.scatter(
        df_filtered,
        x='games',
        y='kda',
        size='winrate',
        color=color_variable,  # Dynamically colored by Team or League
        hover_name='name',
        size_max=45,
        opacity=0.8,
        title='KDA vs. Games Played'
    )

    fig3.update_layout(
        xaxis_title='Games Played',
        yaxis_title='KDA',
        legend_title=legend_title
    )
    st.plotly_chart(fig3, use_container_width=True)
