import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def show_impact_chart(df: pd.DataFrame, selected_role: str):
    """GPM vs. Kill Participation, sized by Impact Score."""

    st.subheader("GPM vs. Kill Participation (Team Impact)")

    if selected_role == "ALL":
        color_variable = 'team_name'
        grouping_title = "Team Name"
    else:
        color_variable = 'league'
        grouping_title = "League"

    available_groups = sorted(df[color_variable].unique())
    selected_groups = st.multiselect(
        f"Filter Players by {grouping_title}:",
        options=available_groups,
        default=available_groups,
        key=f"early_game_filter_{color_variable}"  # Unique key for multiselect
    )

    # Filter the DataFrame based on user selection
    df_filtered = df[df[color_variable].isin(selected_groups)]

    if df_filtered.empty:
        st.warning(f"No data available for the selected {grouping_title}(s).")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    fig = px.scatter(
        df_filtered, x='gpm', y='kp', size='impact_score', color='impact_score',color_continuous_scale='Plasma_r', hover_data='name'
    )
    # Highlight highest impact players
    top_impact_players = df.sort_values(by='impact_score', ascending=False).head(3)
    for index, row in top_impact_players.iterrows():
        ax.text(row['gpm'] + 2, row['kp'], row['name'], fontsize=10, weight='bold', color='red')

    ax.set_title('GPM vs. Kill Participation (Teamfight & Resource Impact)', fontsize=16)
    ax.set_xlabel('Gold Per Minute (GPM)')
    ax.set_ylabel('Kill Participation (KP)')
    st.plotly_chart(fig)
