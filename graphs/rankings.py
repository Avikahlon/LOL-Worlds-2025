import streamlit as st
import pandas as pd


def show_rankings(df: pd.DataFrame):
    """Displays the KDA and Impact Score rankings side-by-side."""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("KDA")
        df_kda_rank = df.sort_values(by='kda', ascending=False).head(5)
        n = 1
        for i, row in df_kda_rank.iterrows():
            st.markdown(f"{n}. {row['name']} - KDA: **{row['kda']:.2f}**")
            n += 1

    with col2:
        st.subheader("Impact Score (Resource & Teamfight)")
        df_impact_rank = df.sort_values(by='impact_score', ascending=False).head(5)
        n = 1
        for i, row in df_impact_rank.iterrows():
            st.markdown(f"{n}. {row['name']} - Score: **{row['impact_score']:.0f}**")
            n += 1