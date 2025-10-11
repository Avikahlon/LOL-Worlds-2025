import streamlit as st
from typing import Dict, Any

WORLDS_TEAMS_DATA: Dict[str, Any] = {
    "LCK (Korea)": {
        "image": "images/lck.png",
        "teams": [
            {
                "name": "Gen.G",
                "logo": "images/geng.png",
                "summary": "Strongest team entering Worlds 2025, winning **MSI 2025** and completely dominating the LCK season. They secured the 1st seed after losing only two domestic games all year.",
            },
            {
                "name": "Hanwha Life Esports (HLE)",
                "logo": "images/hle.png",
                "summary": "Winners of **First Stand 2025** and the **LCK Cup**, they looked incredibly promising early in the year. Despite missing MSI, they finished the LCK season as the 2nd seed.",
            },
            {
                "name": "KT Rolster",
                "logo": "images/kt.png",
                "summary": "A surprise qualification. Considered a tier below the top LCK teams for most of the year, KT managed to secure the **3rd seed** after defeating Gen.G in a crucial, high-stakes Regional Finals match.",
            },
            {
                "name": "T1",
                "logo": "images/t1.png",
                "summary": "Despite finishing 4th in the LCK and 2nd at MSI, T1 remains an international favorite. They must defeat IG in the final **Worlds Qualifying Match** to secure their spot, showcasing their volatile, high-ceiling potential.",
            },
        ],
    },
    "LPL (China)": {
        "image": "images/lpl.png",
        "teams": [
            {
                "name": "Bilibili Gaming (BLG)",
                "logo": "images/blg.png",
                "summary": "The **LPL Grand Finals Champion** and likely the strongest Chinese team entering Worlds. They secured the title despite looking inconsistent throughout the year, redeeming an earlier MSI 2025 loss to AL.",
            },
            {
                "name": "Top Esports (TES)",
                "logo": "images/tes.png",
                "summary": "Consistent finalists, securing **2nd place in the LPL Grand Finals**. Known for often losing high-stakes final matches and carry a reputation for potentially 'choking' on the international stage, having missed MSI.",
            },
            {
                "name": "Anyone's Legend (AL)",
                "logo": "images/al.png",
                "summary": "The **early-season kings**, winning the Demacia Cup and showing immense promise at MSI where they nearly defeated GenG and T1. A late-season dip saw them miss the LPL Grand Finals, but they remain a high seed.",
            },
            {
                "name": "Invictus Gaming (IG)",
                "logo": "images/ig.png",
                "summary": "A mid-tier team for much of the year, IG possesses a solid core with high individual ceilings. They secured the **4th seed** and must face T1 in the Worlds Qualifying Match to secure their final tournament spot.",
            },
        ],
    },
    "LEC (Europe)": {
        "image": "images/lec.png",
        "teams": [
            {
                "name": "G2 Esports",
                "logo": "images/g2.png",
                "summary": "Europe's strongest team. Finished 2nd in the Winter and Spring Splits before convincingly winning the **Summer Split**. Despite an early exit at MSI, they are the LEC's best hope.",
            },
            {
                "name": "MKOI",
                "logo": "images/mkoi.png",
                "summary": "The surprising **LEC Spring Split Champions**. They looked dominant for a time but had an early MSI exit and were eliminated by G2 in the Summer Split, securing a 2nd place finish",
            },
            {
                "name": "Fnatic",
                "logo": "images/fnatic.png",
                "summary": "A consistently solid presence in the LEC, placing 3rd-4th throughout the year. With new midlaner Poby(The GOST), the veteran organization secured a Worlds berth but are not favored for a deep tournament run.",
            },
        ],
    },
    "LTA (Americas)": {
        "image": "images/lta.png",
        "teams": [
            {
                "name": "FlyQuest",
                "logo": "images/fly.png",
                "summary": "The clear **best team in the region**, winning every LTA Split this year. They are considered by many to be the strongest Western team and performed well at MSI, and also the team that nearly defeated Gen.G. last Worlds",
            },
            {
                "name": "Vivo Keyd Stars (VK)",
                "logo": "images/vkd.png",
                "summary": "The **CBLOL (LTA South) Champion** who secured 2nd place overall in the LTA Championship. Lost the final to FlyQuest but represent a strong regional force entering the tournament.",
            },
            {
                "name": "100 Thieves",
                "logo": "images/100t.png",
                "summary": "Finished 2nd in the LCS North division and 3rd overall in the LTA Championship. Qualified for Worlds without winning a major title.",
            },
        ],
    },
    "LCP (Asia-Pacific)": {
        "image": "images/lcp.png",
        "teams": [
            {
                "name": "CTBC Flying Oyster (CFO)",
                "logo": "images/cfo.png",
                "summary": "The best team in the PCS all year. Showed impressive international form at MSI 2025, taking the then-in-form T1 to five games, highlighting their potential with exciting young players.",
            },
            {
                "name": "Team Secret Whales (TSW)",
                "logo": "images/tsw.png",
                "summary": "The consistent second-best team in the PCS, always finishing just behind CFO. Secured their Worlds spot through consistent seasonal performance and stability.",
            },
            {
                "name": "PSG Talon",
                "logo": "images/psgt.png",
                "summary": "A mid-tier PCS team that secured their Worlds slot via the final qualifying path. They are not expected to be major contenders but are capable of upset wins.",
            },
        ],
    },
}


def show_overview():
    """
    Renders the Worlds Overview page, displaying teams, logos, and achievements
    organized by League using Streamlit tabs.
    """
    st.title("Worlds 2025 Team Overview")
    st.markdown(
        """
        Welcome to the Worlds breakdown! Below is a quick glance at the major teams 
        and their key domestic achievements for the year, organized by their regional league.
        """
    )

    tabs = st.tabs(list(WORLDS_TEAMS_DATA.keys()))

    for i, (league_name, league_data) in enumerate(WORLDS_TEAMS_DATA.items()):
        with tabs[i]:
            logo_col, name_col = st.columns([1, 6])

            with logo_col:
                st.image(league_data["image"], width=100)

            with name_col:
                st.header(league_name)
            for team in league_data["teams"]:
                st.markdown("---")

                col1, col2 = st.columns([1, 6])

                with col1:
                    st.image(team["logo"], width=70)

                with col2:
                    st.subheader(team["name"])
                    st.markdown(f"*{team['summary']}*")

            st.markdown("---")