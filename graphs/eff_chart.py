import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def show_efficiency_chart(df: pd.DataFrame, selected_role: str):
    """
    Renders DPM vs. CSM chart, highlighting efficiency and damage output.

    Colors the chart by team if 'ALL' roles are selected, or by league
    if a specific role is selected.
    """
    st.subheader("Farming Efficiency (CSM) vs. Damage Output (DPM)")

    if selected_role == "ALL":
        color_variable = 'team_name'
        grouping_title = "Team Name"
    else:
        color_variable = 'league'
        grouping_title = "League"

    available_groups = sorted(df[color_variable].unique())
    selected_groups = st.multiselect(
        f"Filter Players by {grouping_title} for Efficiency Chart:",
        options=available_groups,
        default=available_groups,
        key=f"efficiency_filter_{color_variable}"  # Unique key to avoid conflict
    )

    # Filter the DataFrame based on user selection
    df_filtered = df[df[color_variable].isin(selected_groups)]

    if df_filtered.empty:
        st.warning(f"No data available for the selected {grouping_title}(s).")
        return

    fig = px.scatter(
        df_filtered,
        x='dpm',
        y='csm',
        size='games',
        color=color_variable,  # Dynamic coloring
        hover_name='name',
        hover_data=['team_name', 'league', 'csm', 'dpm', 'kp'],
        title=f'Damage Per Minute (DPM) vs. CS Per Minute (CSM) Colored by {grouping_title}'
    )

    fig.update_layout(
        xaxis_title="Damage Per Minute (DPM)",
        yaxis_title="CS Per Minute (CSM)",
        legend_title=grouping_title,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
