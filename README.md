# ⚔️ League of Legends Player Stats Analyzer (S15)
This project provides a comprehensive data analysis and visualization tool for professional League of Legends player performance, specifically targeting data from the competitive season S15 for players and teams competing in the upcoming LOL Worlds 2025. It uses Python for data processing and Streamlit for an interactive web-based visualization application.

# ✨ Features
Performance Metrics: Calculation and display of essential KPIs including KDA, GPM, Kill Participation (KP), and a composite Impact Score.

Early Game Dominance: Visualizations for Gold Difference at 15 minutes (GD15) versus CS Difference at 15 minutes (CSD15).

Ranking Leaderboards: Detailed rankings for stats like Solo Kills, Average Kills/Assists, Damage Share, and Vision Score.

Global Origin Map: A Choropleth map using Plotly to show the geographical distribution of players by their country of origin.

Modular Design: Separated logic for data fetching, analysis, and different visualization types.

# 🛠️ Setup and Prerequisites
To run this project, you need to have Python 3.8+ installed along with the following libraries:

|Library |Purpose |
|--------|--------|
|pandas|Data manipulation and cleaning
|streamlit|Web application framework (main UI)|
|plotly|Interactive charting (used in early_game_chart.py and misc.py)|
|seaborn, matplotlib|Static charting for the notebook and some Streamlit visuals|
|sqlalchemy|Database connector|
