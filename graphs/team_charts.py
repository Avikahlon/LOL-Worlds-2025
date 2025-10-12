import streamlit as st
import pandas as pd
import plotly.express as px

METRIC_GROUPS = {
    "Objectives & Kills": {
        'baron_per_game': 'Barons/Game',
        'drags_per_game': 'Dragons/Game',
        'kills_per_game': 'Kills/Game',
        'deaths_per_game': 'Deaths/Game',
        'plates_per_game': 'Plates/Game',
    },
    "First Control & Percentage": {
        'fb_pct': 'First Blood %',
        'ft_pct': 'First Turret %',
        'fos_pct': 'Feats of Strength %',
        'atak_pct': 'Atakhan %',
        'drag_pct': 'Dragon %',
        'baron_pct': 'Baron %',
    },
    "Efficiency & Economy": {
        'dpm': 'DPM',
        'gpm': 'GPM',
        'cspm': 'CSPM',
        'gdm': 'Gold Diff/Min',
    }
}

REGION_MAP = {
    "Custom Selection": None, # Default option to enable manual multiselect
    "All Teams": None, # Will select all teams available
    "China (LPL)": ["CN"],
    "Korea (LCK)": ["KR"],
    "Europe (LEC)": ["EUW"],
    # Grouping NA and LAT into Americas
    "Americas": ["NA", "LAT"],
    # Grouping Taiwan and Vietnam into Asia Pacific
    "Asia Pacific": ["TW", "VN"]
}
REGION_OPTIONS = list(REGION_MAP.keys())

def show_team_performance_charts(df_teams: pd.DataFrame):
    """
    Generates three distinct charts (Bar, Scatter, Polar) to compare teams
    across Objectives, Efficiency, and Percentage Control metrics.
    """
    st.title("Team Performance Profiles (Multi-Chart View)")
    st.info(
        "Compare teams using visualizations optimized for different metric types: Ranking, Trade-offs, and Balance.")

    if df_teams.empty:
        st.warning("Team data is not available. Please ensure data handler is loading 'teams_staging'.")
        return

    group_filter = st.selectbox(
        "Compare teams by grouping:",
        options=REGION_OPTIONS,
        index=0  # Default to Custom Selection
    )

    all_teams = df_teams['name'].unique().tolist()

    teams_to_show = []

    if group_filter == "Custom Selection":
        is_multiselect_disabled = False
        sort_col = 'kills_per_game' if 'kills_per_game' in df_teams.columns else df_teams.columns[0]
        default_teams = df_teams.sort_values(
            by=sort_col, ascending=False
        )['name'].head(10).tolist()

        # Multiselect is enabled and controls the list
        selected_teams = st.multiselect(
            "Select teams to compare (Applies to all charts below):",
            options=all_teams,
            default=default_teams,
            key='all_team_charts_select',
            disabled=is_multiselect_disabled
        )
        teams_to_show = selected_teams

    else:
        is_multiselect_disabled = True
        st.caption(f"Showing all teams from the '{group_filter}' region(s).")

        # Get the list of region codes from the map
        region_codes = REGION_MAP[group_filter]

        if region_codes is None or group_filter == "All Teams":
            # Show ALL available teams
            teams_to_show = all_teams
        else:
            # Filter by the specified list of region codes (requires 'league' column)
            if 'region' in df_teams.columns:
                # UPDATED: Use isin() to filter by the list of region codes
                teams_to_show = df_teams[df_teams['region'].isin(region_codes)]['name'].unique().tolist()
            else:
                st.error(
                    f"Error: Cannot filter by region '{group_filter}'. 'league' column is missing from team data. The codes expected were: {region_codes}")
                return

    if len(teams_to_show) < 1:
        st.warning(f"No teams selected or found for the current filter: **{group_filter}**.")
        return

    # Filter the DataFrame using the determined list of teams
    df_filtered = df_teams[df_teams['name'].isin(teams_to_show)].copy()

    # Fill NaN values with 0 for metrics being plotted
    df_filtered = df_filtered.fillna(0)

    # --- CHART 1: Objectives & Kills (Horizontal Bar Chart) ---
    st.markdown(f"---")
    st.subheader("1. Objective Control Ranking (Bar Chart)")
    st.caption("Ranks teams by selected objective acquisition per game.")

    obj_metrics = METRIC_GROUPS["Objectives & Kills"]
    rank_metric_key = st.selectbox(
        "Select objective metric to rank by:",
        list(obj_metrics.keys()),
        format_func=lambda x: obj_metrics[x],
        key='obj_rank_select'
    )

    df_sorted = df_filtered.sort_values(by=rank_metric_key, ascending=True)

    fig_bar = px.bar(
        df_sorted,
        x=rank_metric_key,
        y='name',
        orientation='h',
        color='name',
        title=f"Team Ranking by {obj_metrics[rank_metric_key]}",
        labels={'name': 'Team', rank_metric_key: obj_metrics[rank_metric_key]},
        template="plotly_white"
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- CHART 2: Efficiency & Economy (Scatter Plot) ---
    st.markdown(f"---")
    st.subheader("2. Economic Efficiency vs. Damage Output (Scatter Plot)")
    st.caption("Identifies teams that turn resources (GPM) into damage (DPM). Top-right is most efficient.")

    eff_metrics = METRIC_GROUPS["Efficiency & Economy"]

    fig_scatter = px.scatter(
        df_filtered,
        x='gpm',
        y='dpm',
        color='name',
        size='cspm',  # Use Gold Difference per minute for bubble size
        hover_data=['name', 'cspm', 'gdm'],
        size_max=45,
        title='DPM vs. GPM (Bubble size = CS per Minute)',
        labels={'gpm': eff_metrics['gpm'], 'dpm': eff_metrics['dpm']},
        template="plotly_dark"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- CHART 3: First Control & Percentage (Polar Chart) ---
    st.markdown(f"---")
    st.subheader("3. First Control & Early Game Priority (Polar Chart)")
    st.caption("Visualizes the balance of early-game objectives (First Blood, Turret, Dragon).")

    pct_metrics = METRIC_GROUPS["First Control & Percentage"]
    metrics_to_plot = list(pct_metrics.keys())

    df_plot = df_filtered[['name'] + metrics_to_plot]
    df_melted = df_plot.melt(
        id_vars='name',
        value_vars=metrics_to_plot,
        var_name='Metric',
        value_name='Value'
    )
    df_melted['Metric'] = df_melted['Metric'].apply(lambda x: pct_metrics.get(x, x))

    fig_polar = px.line_polar(
        df_melted,
        r='Value',
        theta='Metric',
        color='name',
        line_close=True,
        template="plotly_dark",
        title="Team Early Game Percentage Control"
    )

    # fig_polar.update_traces(fill='toself', opacity=0.4)
    max_val = df_melted['Value'].max()
    fig_polar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max_val * 1.1])
        )
    )
    st.plotly_chart(fig_polar, use_container_width=True)
