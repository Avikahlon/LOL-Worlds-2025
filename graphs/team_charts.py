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
        'csm': 'CSM',
        'gdm': 'Gold Diff/Min',
    }
}


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

    # --- 1. Shared Team Selection ---
    all_teams = df_teams['name'].unique().tolist()

    sort_col = 'kills_per_game' if 'kills_per_game' in df_teams.columns else df_teams.columns[0]
    # CHANGED: Use 'name' instead of 'team_name'
    default_teams = df_teams.sort_values(
        by=sort_col, ascending=False
    )['name'].head(5).tolist()

    selected_teams = st.multiselect(
        "Select teams to compare (Applies to all charts below):",
        options=all_teams,
        default=default_teams,
        key='all_team_charts_select'
    )

    if len(selected_teams) < 1:
        st.warning("Please select at least one team for analysis.")
        return

    df_filtered = df_teams[df_teams['name'].isin(selected_teams)].copy()

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
        size='gdm',  # Use Gold Difference per minute for bubble size
        hover_data=['name', 'gdm'],
        size_max=45,
        title='DPM vs. GPM (Bubble size = Gold Difference per Minute)',
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
