import streamlit as st
import pandas as pd
import plotly.express as px

def show_early_game_chart(df: pd.DataFrame, selected_role: str):
    """
    Renders GD15 vs. CSD15 chart.

    Colors the chart by team if 'ALL' roles are selected, or by league
    if a specific role is selected, to visually confirm farming vs. team-play leads.
    """
    st.subheader("Early Game Lead Comparison (GD15 vs. CSD15)")

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

    fig = px.scatter(
        df_filtered,
        x='csd15',
        y='gd15',
        size='games',
        color=color_variable,  # Dynamic coloring
        hover_name='name',
        hover_data=['team_name', 'league', 'games'],
        title=f'Gold Difference (GD15) vs. CS Difference (CSD15) Colored by {grouping_title}'
    )

    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="gray",
                  annotation_text="CS Neutral", annotation_position="bottom left")

    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray",
                  annotation_text="Gold Neutral", annotation_position="top left")

    fig.add_annotation(
        x=df_filtered['csd15'].max() * 0.9, y=df_filtered['gd15'].min() * 0.9,
        text="High CSD, Low GD (Farming Lead Lost)", showarrow=False, bgcolor="rgba(255, 0, 0, 0.2)"
    )
    fig.add_annotation(
        x=df_filtered['csd15'].max() * 0.9, y=df_filtered['gd15'].max() * 0.9,
        text="Dominant Leads (Farming & Kills)", showarrow=False, bgcolor="rgba(0, 255, 0, 0.2)"
    )

    fig.update_layout(
        xaxis_title="CS Difference at 15 Minutes (CSD15)",
        yaxis_title="Gold Difference at 15 Minutes (GD15)",
        legend_title=grouping_title,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)