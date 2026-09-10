import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone

st.set_page_config(page_title="Graph Detectives", page_icon="🔎", layout="wide")

st.title("🔎 Graph Detectives: Exponential & Logarithmic Graphs")
st.caption("A collaborative Streamlit activity for exploring graph families, properties, inverses, and transformations.")
# Dropdowns use Unicode math labels because Streamlit selectboxes do not render LaTeX.

with st.sidebar:
    st.header("Team setup")
    team_name = st.text_input("Team name", value="Team 1")

    # Students enter their own names instead of using placeholder names.
    st.markdown("**Team members**")
    student_1 = st.text_input("Student 1 name", placeholder="Enter name", key="student_1")
    student_2 = st.text_input("Student 2 name", placeholder="Enter name", key="student_2")
    student_3 = st.text_input("Student 3 name", placeholder="Enter name", key="student_3")
    student_4 = st.text_input("Student 4 name", placeholder="Enter name", key="student_4")

    entered_names = [
        name.strip()
        for name in [student_1, student_2, student_3, student_4]
        if name.strip()
    ]
    member_names = "\n".join(entered_names)

    st.divider()
    stage = st.radio(
        "Choose activity",
        [
            "1. Warm-up",
            "2. Sort the Graphs",
            "3. Match Equation & Properties",
            "4. Graph Passport",
            "5. Find the Inverse Partner",
            "6. Transformation Lab",
            "7. Spot the Mistake",
            "8. Mystery Graph",
            "9. Exit Ticket",
            "10. Congratulations & Feedback",
        ],
    )

st.subheader(f"{team_name}")

# ---------- helpers ----------
def clean_axes(ax):
    ax.axhline(0, linewidth=0.8)
    ax.axvline(0, linewidth=0.8)
    ax.grid(alpha=0.2)
    ax.set_xlim(-4, 5)
    ax.set_ylim(-4, 6)
    ax.set_xlabel("x")
    ax.set_ylabel("y")


def exp_plot(base):
    x = np.linspace(-4, 4, 500)
    y = base ** x
    fig, ax = plt.subplots(figsize=(4, 3))
    clean_axes(ax)
    ax.plot(x, y)
    return fig


def log_plot(base):
    x = np.linspace(0.05, 5, 500)
    y = np.log(x) / np.log(base)
    fig, ax = plt.subplots(figsize=(4, 3))
    clean_axes(ax)
    ax.plot(x, y)
    return fig


def transformed_log_plot():
    x = np.linspace(2.05, 8, 500)
    y = np.log2(x - 2) + 1
    fig, ax = plt.subplots(figsize=(6, 4))
    clean_axes(ax)
    ax.set_xlim(-1, 9)
    ax.set_ylim(-4, 6)
    ax.plot(x, y)
    ax.axvline(2, linestyle="--", linewidth=1)
    return fig


def feedback(correct, message="Correct! 🎉"):
    if correct:
        st.success(message)
    else:
        st.error("Not quite yet. Discuss your reasoning and try again.")


# ---------- results tracking + Google Sheets ----------
SCORE_MAX = {
    "Sort the Graphs": 4,
    "Match Equation & Properties": 4,
    "Graph Passport": 14,
    "Find the Inverse Partner": 5,
    "Transformation Lab": 9,
    "Spot the Mistake": 1,
    "Mystery Graph": 6,
    "Exit Ticket": 1,
}

for _activity in SCORE_MAX:
    st.session_state.setdefault(f"score::{_activity}", 0)


def save_score(activity, score):
    """Store the team's latest score for an activity."""
    st.session_state[f"score::{activity}"] = max(
        0, min(int(score), SCORE_MAX[activity])
    )


def score_for(activity):
    return st.session_state.get(f"score::{activity}", 0)


def overall_score():
    earned = sum(score_for(activity) for activity in SCORE_MAX)
    possible = sum(SCORE_MAX.values())
    percent = round((earned / possible) * 100, 1) if possible else 0.0
    return earned, possible, percent


@st.cache_resource
def get_results_worksheet():
    """Connect to the private Google Sheet defined in Streamlit Secrets."""
    service_info = dict(st.secrets["gcp_service_account"])

    # Works whether the private key was saved with literal \n characters
    # or as real line breaks in Streamlit Secrets.
    if "private_key" in service_info:
        service_info["private_key"] = service_info["private_key"].replace("\\n", "\n")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(
        service_info,
        scopes=scopes,
    )
    client = gspread.authorize(credentials)

    spreadsheet_id = st.secrets["google_sheet"]["spreadsheet_id"]
    worksheet_name = st.secrets["google_sheet"].get("worksheet_name", "Results")

    spreadsheet = client.open_by_key(spreadsheet_id)

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows=1000,
            cols=30,
        )

    headers = [
        "Submitted UTC",
        "Team Name",
        "Student 1",
        "Student 2",
        "Student 3",
        "Student 4",
        "Sort the Graphs",
        "Match Equation & Properties",
        "Graph Passport",
        "Find the Inverse Partner",
        "Transformation Lab",
        "Spot the Mistake",
        "Mystery Graph",
        "Exit Ticket",
        "Total Score",
        "Total Possible",
        "Overall Percentage",
        "Game Rating",
        "Improvement Suggestion",
        "Exit Q1 - Recognize exponential",
        "Exit Q2 - Recognize logarithmic",
        "Exit Q3 - Relationship",
        "Exit Q4 - Inverse point",
        "Exit Q5 - Understanding",
    ]

    existing = worksheet.row_values(1)
    if existing != headers:
        worksheet.update("A1:X1", [headers])

    return worksheet


def submit_team_results(rating, improvement):
    worksheet = get_results_worksheet()
    earned, possible, percent = overall_score()

    names = [student_1.strip(), student_2.strip(), student_3.strip(), student_4.strip()]

    row = [
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        team_name.strip(),
        names[0],
        names[1],
        names[2],
        names[3],
        f'{score_for("Sort the Graphs")}/{SCORE_MAX["Sort the Graphs"]}',
        f'{score_for("Match Equation & Properties")}/{SCORE_MAX["Match Equation & Properties"]}',
        f'{score_for("Graph Passport")}/{SCORE_MAX["Graph Passport"]}',
        f'{score_for("Find the Inverse Partner")}/{SCORE_MAX["Find the Inverse Partner"]}',
        f'{score_for("Transformation Lab")}/{SCORE_MAX["Transformation Lab"]}',
        f'{score_for("Spot the Mistake")}/{SCORE_MAX["Spot the Mistake"]}',
        f'{score_for("Mystery Graph")}/{SCORE_MAX["Mystery Graph"]}',
        f'{score_for("Exit Ticket")}/{SCORE_MAX["Exit Ticket"]}',
        earned,
        possible,
        percent,
        rating,
        improvement.strip(),
        st.session_state.get("exit_e1", ""),
        st.session_state.get("exit_e2", ""),
        st.session_state.get("exit_e3", ""),
        st.session_state.get("exit_e4", ""),
        st.session_state.get("exit_e5", ""),
    ]

    # Prevent accidental duplicate submissions after a browser refresh.
    # If the same team name + student names already exist, update that row instead.
    existing_rows = worksheet.get_all_values()
    submission_key = [
        team_name.strip().casefold(),
        *[name.casefold() for name in names],
    ]

    matching_row = None
    for row_number, existing_row in enumerate(existing_rows[1:], start=2):
        padded = existing_row + [""] * max(0, 6 - len(existing_row))
        existing_key = [
            padded[1].strip().casefold(),
            padded[2].strip().casefold(),
            padded[3].strip().casefold(),
            padded[4].strip().casefold(),
            padded[5].strip().casefold(),
        ]
        if existing_key == submission_key:
            matching_row = row_number
            break

    if matching_row:
        worksheet.update(
            f"A{matching_row}:X{matching_row}",
            [row],
            value_input_option="USER_ENTERED",
        )
    else:
        worksheet.append_row(row, value_input_option="USER_ENTERED")

    return earned, possible, percent


def show_progress():
    earned, possible, percent = overall_score()
    st.progress(percent / 100 if possible else 0)
    st.caption(f"Recorded performance so far: {earned}/{possible} points ({percent}%).")



# ---------- stage 1 ----------
if stage == "1. Warm-up":
    st.header("1. Warm-up")
    st.markdown("**Mission:** Share one idea your group already knows about exponential or logarithmic graphs.")
    responses = []
    names = [n.strip() for n in member_names.splitlines() if n.strip()]
    if not names:
        st.warning("Please enter at least one student name in the sidebar before starting the warm-up.")
    else:
        cols = st.columns(min(4, len(names)))
        for i, name in enumerate(names):
            with cols[i % len(cols)]:
                responses.append(st.text_area(f"{name}'s idea", key=f"warm_{i}"))
    st.info("Discuss: What visual feature most clearly separates an exponential graph from a logarithmic graph?")

# ---------- stage 2 ----------
elif stage == "2. Sort the Graphs":
    st.header("2. Sort the Graphs")
    st.markdown("Classify each unlabeled graph as **Exponential** or **Logarithmic**.")

    graph_defs = [
        ("A", "Exponential", exp_plot(2)),
        ("B", "Exponential", exp_plot(0.5)),
        ("C", "Logarithmic", log_plot(2)),
        ("D", "Logarithmic", log_plot(0.5)),
    ]
    answers = {}
    cols = st.columns(2)
    for idx, (label, truth, fig) in enumerate(graph_defs):
        with cols[idx % 2]:
            st.markdown(f"### Graph {label}")
            st.pyplot(fig, clear_figure=True)
            answers[label] = st.radio(
                f"Graph {label} is...",
                ["Choose", "Exponential", "Logarithmic"],
                horizontal=True,
                key=f"sort_{label}",
            )

    if st.button("Check sorting"):
        stage_score = sum(
            answers[label] == truth for label, truth, _ in graph_defs
        )
        save_score("Sort the Graphs", stage_score)
        ok = stage_score == SCORE_MAX["Sort the Graphs"]
        feedback(ok, "Excellent — all graph families are correct.")
        st.caption(f"Score recorded: {stage_score}/4")

    st.markdown("### Team reasoning")
    st.text_area("How can you recognize an exponential graph?")
    st.text_area("How can you recognize a logarithmic graph?")

# ---------- stage 3 ----------
elif stage == "3. Match Equation & Properties":
    st.header("3. Match Equation & Properties")
    st.markdown("Match each graph to an equation, then identify its key properties.")

    # Use plain Unicode text inside dropdowns because Streamlit selectboxes
    # do not render LaTeX.
    items = [
        (
            "A",
            exp_plot(2),
            "y = 2ˣ",
            "Horizontal asymptote y = 0",
            "Passes through (0, 1)",
            "Increasing",
        ),
        (
            "B",
            exp_plot(0.5),
            "y = (½)ˣ",
            "Horizontal asymptote y = 0",
            "Passes through (0, 1)",
            "Decreasing",
        ),
        (
            "C",
            log_plot(2),
            "y = log₂ x",
            "Vertical asymptote x = 0",
            "Passes through (1, 0)",
            "Increasing",
        ),
        (
            "D",
            log_plot(0.5),
            "y = log₍₁⁄₂₎ x",
            "Vertical asymptote x = 0",
            "Passes through (1, 0)",
            "Decreasing",
        ),
    ]

    eq_options = [
        "y = 2ˣ",
        "y = (½)ˣ",
        "y = log₂ x",
        "y = log₍₁⁄₂₎ x",
    ]

    prop_options = [
        "Horizontal asymptote y = 0",
        "Vertical asymptote x = 0",
        "Passes through (0, 1)",
        "Passes through (1, 0)",
        "Increasing",
        "Decreasing",
    ]

    for label, fig, eq, p1, p2, p3 in items:
        with st.expander(f"Graph {label}", expanded=True):
            c1, c2 = st.columns([1, 1])

            with c1:
                st.pyplot(fig, clear_figure=True)

            with c2:
                eq_choice = st.selectbox(
                    "Equation",
                    ["Choose"] + eq_options,
                    key=f"eq_{label}",
                )
                props = st.multiselect(
                    "Select 3 correct properties",
                    prop_options,
                    key=f"prop_{label}",
                )

                if st.button(f"Check Graph {label}", key=f"btn_{label}"):
                    eq_ok = eq_choice == eq
                    props_ok = set(props) == {p1, p2, p3}
                    graph_ok = eq_ok and props_ok
                    st.session_state[f"stage3::{label}"] = graph_ok
                    stage_score = sum(
                        bool(st.session_state.get(f"stage3::{g}", False))
                        for g in ["A", "B", "C", "D"]
                    )
                    save_score("Match Equation & Properties", stage_score)
                    feedback(graph_ok)
                    st.caption(f"Stage score recorded: {stage_score}/4")

# ---------- stage 4 ----------
elif stage == "4. Graph Passport":
    st.header("4. Graph Passport")
    st.markdown("Compare the two functions below.")

    c1, c2 = st.columns(2)
    with c1:
        st.latex(r"f(x)=2^x")
    with c2:
        st.latex(r"g(x)=\log_2 x")

    # Display-friendly Unicode options for selectboxes.
    features = [
        ("Function type", "Exponential", "Logarithmic"),
        ("Domain", "(−∞, ∞)", "(0, ∞)"),
        ("Range", "(0, ∞)", "(−∞, ∞)"),
        ("x-intercept", "None", "(1, 0)"),
        ("y-intercept", "(0, 1)", "None"),
        ("Asymptote", "y = 0", "x = 0"),
        ("Direction", "Increasing", "Increasing"),
    ]

    choices = [
        "Exponential",
        "Logarithmic",
        "None",
        "Increasing",
        "Decreasing",
        "(−∞, ∞)",
        "(0, ∞)",
        "(0, 1)",
        "(1, 0)",
        "y = 0",
        "x = 0",
    ]

    ok_list = []

    # Header row
    h1, h2, h3 = st.columns([1.4, 1, 1])
    with h1:
        st.markdown("**Feature**")
    with h2:
        st.markdown("**f(x) = 2ˣ**")
    with h3:
        st.markdown("**g(x) = log₂ x**")

    for feat, ans1, ans2 in features:
        a, b, c = st.columns([1.4, 1, 1])

        with a:
            st.markdown(f"**{feat}**")

        with b:
            v1 = st.selectbox(
                f"{feat} for f",
                ["Choose"] + choices,
                key=f"pf_{feat}",
                label_visibility="collapsed",
            )

        with c:
            v2 = st.selectbox(
                f"{feat} for g",
                ["Choose"] + choices,
                key=f"pg_{feat}",
                label_visibility="collapsed",
            )

        ok_list.append(v1 == ans1 and v2 == ans2)

    if st.button("Check passport"):
        passport_score = 0
        for feat, ans1, ans2 in features:
            passport_score += st.session_state.get(f"pf_{feat}") == ans1
            passport_score += st.session_state.get(f"pg_{feat}") == ans2

        save_score("Graph Passport", passport_score)
        feedback(
            passport_score == SCORE_MAX["Graph Passport"],
            "Passport complete — the properties are all correct.",
        )
        st.caption(f"Score recorded: {passport_score}/14")

# ---------- stage 5 ----------
elif stage == "5. Find the Inverse Partner":
    st.header("5. Find the Inverse Partner")
    st.markdown("Pair each exponential function with its logarithmic inverse.")

    pairs = [
        (r"y=2^x", "y = log₂ x"),
        (r"y=3^x", "y = log₃ x"),
        (r"y=10^x", "y = log₁₀ x"),
        (r"y=\left(\frac{1}{2}\right)^x", "y = log₍₁⁄₂₎ x"),
    ]

    inv_options = [
        "y = log₂ x",
        "y = log₃ x",
        "y = log₁₀ x",
        "y = log₍₁⁄₂₎ x",
    ]

    checks = []

    for i, (left_latex, correct_answer) in enumerate(pairs):
        c1, c2 = st.columns([1, 1.3])

        with c1:
            st.latex(left_latex)

        with c2:
            pick = st.selectbox(
                "Inverse partner",
                ["Choose"] + inv_options,
                key=f"inv_{i}",
            )

        checks.append(pick == correct_answer)

    if st.button("Check inverse pairs"):
        pair_score = sum(checks)
        st.session_state["stage5_pairs"] = pair_score
        total_stage5 = pair_score + st.session_state.get("stage5_coordinate", 0)
        save_score("Find the Inverse Partner", total_stage5)
        feedback(
            pair_score == 4,
            "Correct — every exponential function is matched to its logarithmic inverse.",
        )
        st.caption(f"Inverse-pair score recorded: {pair_score}/4")

    st.divider()
    st.subheader("Coordinate Mystery")

    st.latex(r"(0,1),\ (1,2)\text{ are points on }y=2^x")

    q1 = st.selectbox(
        "Which corresponding points lie on the inverse?",
        [
            "Choose",
            "(1, 0) and (2, 1)",
            "(−1, 0) and (−2, 1)",
            "(0, 1) and (1, 2)",
        ],
    )

    q2 = st.radio(
        "What happens to coordinates for inverse functions?",
        [
            "Choose",
            "(x, y) → (y, x)",
            "(x, y) → (−x, y)",
            "(x, y) → (x, −y)",
        ],
        horizontal=True,
    )

    if st.button("Check coordinate mystery"):
        coord_ok = (
            q1 == "(1, 0) and (2, 1)"
            and q2 == "(x, y) → (y, x)"
        )
        st.session_state["stage5_coordinate"] = 1 if coord_ok else 0
        total_stage5 = (
            st.session_state.get("stage5_pairs", 0)
            + st.session_state["stage5_coordinate"]
        )
        save_score("Find the Inverse Partner", total_stage5)
        feedback(coord_ok)
        st.caption(f"Stage score recorded: {total_stage5}/5")

    st.markdown("Inverse-function graphs are reflections across")
    st.latex(r"y=x")

# ---------- stage 6 ----------
elif stage == "6. Transformation Lab":
    st.header("6. Transformation Lab")
    st.markdown("### Exponential parent")
    st.latex(r"y=2^x")

    exp_transforms = [
        (r"y=2^x+3", "Shift up 3"),
        (r"y=2^{x-2}", "Shift right 2"),
        (r"y=-2^x", "Reflect across the x-axis"),
        (r"y=2^{-x}", "Reflect across the y-axis"),
    ]
    options = ["Shift up 3", "Shift right 2", "Reflect across the x-axis", "Reflect across the y-axis"]
    checks = []
    for i, (eq, ans) in enumerate(exp_transforms):
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.latex(eq)
        with c2:
            choice = st.selectbox("Transformation", ["Choose"] + options, key=f"etr_{i}")
        checks.append(choice == ans)
    if st.button("Check exponential transformations"):
        exp_score = sum(checks)
        st.session_state["stage6_exp"] = exp_score
        total_stage6 = (
            exp_score
            + st.session_state.get("stage6_exp_asym", 0)
            + st.session_state.get("stage6_log", 0)
            + st.session_state.get("stage6_log_asym", 0)
        )
        save_score("Transformation Lab", total_stage6)
        feedback(exp_score == 4)
        st.caption(f"Exponential transformation score recorded: {exp_score}/4")

    st.latex(r"y=2^x+3")
    asym = st.text_input("What is the new horizontal asymptote?")
    if st.button("Check asymptote"):
        asym_ok = asym.replace(" ", "") in {"y=3", "3"}
        st.session_state["stage6_exp_asym"] = 1 if asym_ok else 0
        total_stage6 = (
            st.session_state.get("stage6_exp", 0)
            + st.session_state["stage6_exp_asym"]
            + st.session_state.get("stage6_log", 0)
            + st.session_state.get("stage6_log_asym", 0)
        )
        save_score("Transformation Lab", total_stage6)
        feedback(asym_ok)

    st.divider()
    st.markdown("### Logarithmic parent")
    st.latex(r"y=\log_2 x")
    log_transforms = [
        (r"y=\log_2(x-3)", "Shift right 3"),
        (r"y=\log_2x+2", "Shift up 2"),
        (r"y=-\log_2x", "Reflect across the x-axis"),
    ]
    lopts = ["Shift right 3", "Shift up 2", "Reflect across the x-axis"]
    lchecks = []
    for i, (eq, ans) in enumerate(log_transforms):
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.latex(eq)
        with c2:
            choice = st.selectbox("Transformation", ["Choose"] + lopts, key=f"ltr_{i}")
        lchecks.append(choice == ans)
    if st.button("Check logarithmic transformations"):
        log_score = sum(lchecks)
        st.session_state["stage6_log"] = log_score
        total_stage6 = (
            st.session_state.get("stage6_exp", 0)
            + st.session_state.get("stage6_exp_asym", 0)
            + log_score
            + st.session_state.get("stage6_log_asym", 0)
        )
        save_score("Transformation Lab", total_stage6)
        feedback(log_score == 3)
        st.caption(f"Logarithmic transformation score recorded: {log_score}/3")

    st.latex(r"y=\log_2(x-3)")
    new_asym = st.text_input("What is the new vertical asymptote?")
    if st.button("Check log asymptote"):
        log_asym_ok = new_asym.replace(" ", "") in {"x=3", "3"}
        st.session_state["stage6_log_asym"] = 1 if log_asym_ok else 0
        total_stage6 = (
            st.session_state.get("stage6_exp", 0)
            + st.session_state.get("stage6_exp_asym", 0)
            + st.session_state.get("stage6_log", 0)
            + st.session_state["stage6_log_asym"]
        )
        save_score("Transformation Lab", total_stage6)
        feedback(log_asym_ok)
        st.caption(f"Stage score recorded: {total_stage6}/9")

# ---------- stage 7 ----------
elif stage == "7. Spot the Mistake":
    st.header("7. Spot the Mistake")
    st.warning(
        "Alex says: “The logarithmic graph has a horizontal asymptote at y = 0 "
        "because its exponential partner has one.”"
    )
    st.latex(r"y=\log_2 x")
    agree = st.radio("Do you agree?", ["Choose", "Agree", "Disagree"], horizontal=True)
    reason = st.text_area("Explain your reasoning")
    if st.button("Check claim"):
        claim_ok = agree == "Disagree"
        save_score("Spot the Mistake", 1 if claim_ok else 0)
        if claim_ok:
            st.success(
                "Correct. The logarithmic graph has a vertical asymptote at x = 0. "
                "The horizontal asymptote of the exponential graph reflects across y = x."
            )
        else:
            st.error("Revisit the relationship between inverse graphs and their asymptotes.")

# ---------- stage 8 ----------
elif stage == "8. Mystery Graph":
    st.header("8. Mystery Graph 🔐")
    st.markdown("Study the graph without seeing its equation.")
    st.pyplot(transformed_log_plot(), clear_figure=True)

    q_family = st.selectbox("1. Function family", ["Choose", "Exponential", "Logarithmic"])
    q_dir = st.selectbox("2. Increasing or decreasing?", ["Choose", "Increasing", "Decreasing"])
    q_type = st.selectbox("3. Type of asymptote", ["Choose", "Horizontal", "Vertical"])
    q_asym = st.text_input("4. Equation of the asymptote")
    q_parent = st.selectbox(
        "5. Parent function",
        ["Choose", "y = 2ˣ", "y = log₂ x", "y = x²"],
    )
    q_trans = st.multiselect("6. Transformations", ["Shift right 2", "Shift left 2", "Shift up 1", "Shift down 1", "Reflect across x-axis"])
    q_eq = st.text_input("Bonus: Predict an equation")

    if st.button("Check mystery graph"):
        mystery_checks = [
            q_family == "Logarithmic",
            q_dir == "Increasing",
            q_type == "Vertical",
            q_asym.replace(" ", "") in {"x=2", "2"},
            q_parent == "y = log₂ x",
            set(q_trans) == {"Shift right 2", "Shift up 1"},
        ]
        mystery_score = sum(mystery_checks)
        save_score("Mystery Graph", mystery_score)
        basics = mystery_score == SCORE_MAX["Mystery Graph"]

        if basics:
            st.success("Mystery solved! A suitable equation is")
            st.latex(r"y=\log_2(x-2)+1")
        else:
            st.error("Some clues do not match yet. Focus on the vertical asymptote and the position relative to the parent graph.")
        st.caption(f"Score recorded: {mystery_score}/6")

# ---------- stage 9 ----------
elif stage == "9. Exit Ticket":
    st.header("9. Exit Ticket")
    st.markdown("Answer individually or as a team summary.")
    e1 = st.text_area("1. How can you recognize an exponential graph?")
    e2 = st.text_area("2. How can you recognize a logarithmic graph?")
    e3 = st.text_area("3. What is the relationship between exponential and logarithmic functions?")
    st.latex(r"(3,8) \text{ lies on } y=2^x")
    st.latex(r"y=\log_2 x")
    e4 = st.selectbox(
        "Which point lies on the inverse function shown above?",
        ["Choose", "(8, 3)", "(3, 8)", "(−8, 3)", "(8, −3)"],
    )
    e5 = st.text_area("One thing I understand better now is...")

    if st.button("Submit exit ticket"):
        st.session_state["exit_e1"] = e1.strip()
        st.session_state["exit_e2"] = e2.strip()
        st.session_state["exit_e3"] = e3.strip()
        st.session_state["exit_e4"] = e4
        st.session_state["exit_e5"] = e5.strip()

        exit_ok = e4 == "(8, 3)"
        save_score("Exit Ticket", 1 if exit_ok else 0)

        if exit_ok:
            st.success("Exit ticket submitted. The inverse-coordinate answer is correct: $(8,3)$.")
        else:
            st.warning("Exit ticket recorded. Recheck the inverse-coordinate question before finishing.")

    st.info("When you are done, open **10. Congratulations & Feedback** from the sidebar.")

# ---------- stage 10 ----------
elif stage == "10. Congratulations & Feedback":
    st.balloons()
    st.header("🎉 Congratulations, Graph Detective!")
    st.success(f"Well done, {team_name}! You completed the exponential and logarithmic graphs game.")

    st.markdown(
        """
        You explored graph families, matched equations and properties, compared exponential and
        logarithmic functions, found inverse partners, investigated transformations, and solved a
        mystery graph. Great teamwork! ⭐
        """
    )

    st.divider()
    st.subheader("📊 Your recorded performance")

    earned, possible, percent = overall_score()
    st.metric("Overall score", f"{earned}/{possible}", f"{percent}%")
    show_progress()

    score_rows = []
    for activity, max_score in SCORE_MAX.items():
        score_rows.append(
            {
                "Activity": activity,
                "Score": score_for(activity),
                "Possible": max_score,
            }
        )
    st.dataframe(score_rows, use_container_width=True, hide_index=True)

    st.caption(
        "Your teacher will receive the recorded score shown above when your team submits the final results."
    )

    st.divider()
    st.subheader("⭐ Rate the game")

    rating_display = {
        1: "★☆☆☆☆  1 star",
        2: "★★☆☆☆  2 stars",
        3: "★★★☆☆  3 stars",
        4: "★★★★☆  4 stars",
        5: "★★★★★  5 stars",
    }

    rating = st.radio(
        "How would you rate this game?",
        [1, 2, 3, 4, 5],
        format_func=lambda x: rating_display[x],
        horizontal=True,
        index=4,
    )

    improvement = st.text_area(
        "What is one thing we could change or add to make this game better?",
        placeholder="Write one suggestion for improving the game...",
    )

    st.divider()
    st.subheader("📤 Send results to your teacher")

    missing_names = not team_name.strip() or len(entered_names) == 0
    if missing_names:
        st.warning(
            "Enter a team name and at least one student name in the sidebar before submitting."
        )

    already_submitted = st.session_state.get("results_submitted", False)

    if already_submitted:
        st.success(
            "✅ This team's results have already been sent to the teacher's Google Sheet."
        )

    submit_disabled = missing_names or already_submitted

    if st.button(
        "Submit Final Results",
        type="primary",
        disabled=submit_disabled,
        use_container_width=True,
    ):
        try:
            st.session_state["game_rating"] = rating
            st.session_state["game_improvement"] = improvement

            earned, possible, percent = submit_team_results(rating, improvement)
            st.session_state["results_submitted"] = True

            st.success(
                f"✅ Results sent successfully! Final recorded score: "
                f"{earned}/{possible} ({percent}%)."
            )
            st.info(
                "You may now close the app. Your teacher has a copy of your team's names, "
                "performance, rating, and feedback."
            )
        except Exception as exc:
            st.error(
                "The results could not be sent to Google Sheets. "
                "Please tell your teacher before closing the app."
            )
            with st.expander("Technical details for the teacher"):
                st.code(str(exc))

st.divider()
st.caption("Teacher tip: final team results are saved to the private Google Sheet configured in Streamlit Secrets.")
