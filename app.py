import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Graph Detectives", page_icon="🔎", layout="wide")

st.title("🔎 Graph Detectives: Exponential & Logarithmic Graphs")
st.caption("A collaborative Streamlit activity for exploring graph families, properties, inverses, and transformations.")

with st.sidebar:
    st.header("Team setup")
    team_name = st.text_input("Team name", value="Team 1")
    member_names = st.text_area("Members (one per line)", value="Student A\nStudent B\nStudent C\nStudent D")
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

# ---------- stage 1 ----------
if stage == "1. Warm-up":
    st.header("1. Warm-up")
    st.markdown("**Mission:** Share one idea your group already knows about exponential or logarithmic graphs.")
    responses = []
    names = [n.strip() for n in member_names.splitlines() if n.strip()]
    if not names:
        names = ["Student A", "Student B", "Student C", "Student D"]
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
        ok = all(answers[label] == truth for label, truth, _ in graph_defs)
        feedback(ok, "Excellent — all graph families are correct.")

    st.markdown("### Team reasoning")
    st.text_area("How can you recognize an exponential graph?")
    st.text_area("How can you recognize a logarithmic graph?")

# ---------- stage 3 ----------
elif stage == "3. Match Equation & Properties":
    st.header("3. Match Equation & Properties")
    st.markdown("Match each graph to an equation, then identify its key properties.")

    items = [
        ("A", exp_plot(2), r"y=2^x", "Horizontal asymptote $y=0$", "Passes through $(0,1)$", "Increasing"),
        ("B", exp_plot(0.5), r"y=\left(\frac12\right)^x", "Horizontal asymptote $y=0$", "Passes through $(0,1)$", "Decreasing"),
        ("C", log_plot(2), r"y=\log_2 x", "Vertical asymptote $x=0$", "Passes through $(1,0)$", "Increasing"),
        ("D", log_plot(0.5), r"y=\log_{1/2} x", "Vertical asymptote $x=0$", "Passes through $(1,0)$", "Decreasing"),
    ]
    eq_options = [r"y=2^x", r"y=\left(\frac12\right)^x", r"y=\log_2 x", r"y=\log_{1/2} x"]
    prop_options = [
        "Horizontal asymptote $y=0$",
        "Vertical asymptote $x=0$",
        "Passes through $(0,1)$",
        "Passes through $(1,0)$",
        "Increasing",
        "Decreasing",
    ]

    all_ok = True
    for label, fig, eq, p1, p2, p3 in items:
        with st.expander(f"Graph {label}", expanded=True):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.pyplot(fig, clear_figure=True)
            with c2:
                eq_choice = st.selectbox("Equation", ["Choose"] + eq_options, key=f"eq_{label}")
                props = st.multiselect("Select 3 correct properties", prop_options, key=f"prop_{label}")
                eq_ok = eq_choice == eq
                props_ok = set(props) == {p1, p2, p3}
                all_ok = all_ok and eq_ok and props_ok
                if st.session_state.get(f"show_{label}"):
                    feedback(eq_ok and props_ok)
                if st.button(f"Check Graph {label}", key=f"btn_{label}"):
                    st.session_state[f"show_{label}"] = True
                    st.rerun()

# ---------- stage 4 ----------
elif stage == "4. Graph Passport":
    st.header("4. Graph Passport")
    st.markdown("Compare the two functions below.")
    c1, c2 = st.columns(2)
    with c1:
        st.latex(r"f(x)=2^x")
    with c2:
        st.latex(r"g(x)=\log_2 x")

    features = [
        ("Function type", "Exponential", "Logarithmic"),
        ("Domain", r"(-\infty,\infty)", r"(0,\infty)"),
        ("Range", r"(0,\infty)", r"(-\infty,\infty)"),
        ("x-intercept", "None", r"(1,0)"),
        ("y-intercept", r"(0,1)", "None"),
        ("Asymptote", r"y=0", r"x=0"),
        ("Direction", "Increasing", "Increasing"),
    ]
    choices = [
        "Exponential", "Logarithmic", "None", "Increasing", "Decreasing",
        r"(-\infty,\infty)", r"(0,\infty)", r"(0,1)", r"(1,0)", r"y=0", r"x=0"
    ]

    ok_list = []
    for feat, ans1, ans2 in features:
        a, b, c = st.columns([1.4, 1, 1])
        with a:
            st.markdown(f"**{feat}**")
        with b:
            v1 = st.selectbox(f"{feat} for f", ["Choose"] + choices, key=f"pf_{feat}", label_visibility="collapsed")
        with c:
            v2 = st.selectbox(f"{feat} for g", ["Choose"] + choices, key=f"pg_{feat}", label_visibility="collapsed")
        ok_list.append(v1 == ans1 and v2 == ans2)
    if st.button("Check passport"):
        feedback(all(ok_list), "Passport complete — the properties are all correct.")

# ---------- stage 5 ----------
elif stage == "5. Find the Inverse Partner":
    st.header("5. Find the Inverse Partner")
    st.markdown("Pair each exponential function with its logarithmic inverse.")

    pairs = {
        r"y=2^x": r"y=\log_2 x",
        r"y=3^x": r"y=\log_3 x",
        r"y=10^x": r"y=\log_{10} x",
        r"y=\left(\frac12\right)^x": r"y=\log_{1/2} x",
    }
    inv_options = list(pairs.values())
    check = []
    for i, (left, right) in enumerate(pairs.items()):
        c1, c2 = st.columns([1, 1.3])
        with c1:
            st.latex(left.replace("y=", "y="))
        with c2:
            pick = st.selectbox("Inverse partner", ["Choose"] + inv_options, key=f"inv_{i}")
        check.append(pick == right)
    if st.button("Check inverse pairs"):
        feedback(all(check), "Correct — every exponential function is matched to its logarithmic inverse.")

    st.divider()
    st.subheader("Coordinate Mystery")
    st.latex(r"(0,1),\ (1,2) \text{ are points on } y=2^x")
    q1 = st.selectbox("Which corresponding points lie on the inverse?", ["Choose", "(1,0) and (2,1)", "(-1,0) and (-2,1)", "(0,1) and (1,2)"])
    q2 = st.radio("What happens to coordinates for inverse functions?", ["Choose", r"(x,y)\to(y,x)", r"(x,y)\to(-x,y)", r"(x,y)\to(x,-y)"], horizontal=True)
    if st.button("Check coordinate mystery"):
        feedback(q1 == "(1,0) and (2,1)" and q2 == r"(x,y)\to(y,x)")
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
        feedback(all(checks))

    asym = st.text_input("For $y=2^x+3$, what is the new horizontal asymptote?")
    if st.button("Check asymptote"):
        feedback(asym.replace(" ", "") in {"y=3", "3"})

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
        feedback(all(lchecks))

    new_asym = st.text_input(r"For $y=\log_2(x-3)$, what is the new vertical asymptote?")
    if st.button("Check log asymptote"):
        feedback(new_asym.replace(" ", "") in {"x=3", "3"})

# ---------- stage 7 ----------
elif stage == "7. Spot the Mistake":
    st.header("7. Spot the Mistake")
    st.warning("Alex says: ‘The graph of $y=\\log_2 x$ has a horizontal asymptote $y=0$ because its exponential partner has one.’")
    agree = st.radio("Do you agree?", ["Choose", "Agree", "Disagree"], horizontal=True)
    reason = st.text_area("Explain your reasoning")
    if st.button("Check claim"):
        if agree == "Disagree":
            st.success("Correct. $y=\\log_2 x$ has a vertical asymptote at $x=0$. The horizontal asymptote of the exponential graph reflects across $y=x$.")
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
    q_parent = st.selectbox("5. Parent function", ["Choose", r"y=2^x", r"y=\log_2x", r"y=x^2"])
    q_trans = st.multiselect("6. Transformations", ["Shift right 2", "Shift left 2", "Shift up 1", "Shift down 1", "Reflect across x-axis"])
    q_eq = st.text_input("Bonus: Predict an equation")

    if st.button("Check mystery graph"):
        basics = (
            q_family == "Logarithmic"
            and q_dir == "Increasing"
            and q_type == "Vertical"
            and q_asym.replace(" ", "") in {"x=2", "2"}
            and q_parent == r"y=\log_2x"
            and set(q_trans) == {"Shift right 2", "Shift up 1"}
        )
        if basics:
            st.success("Mystery solved! A suitable equation is")
            st.latex(r"y=\log_2(x-2)+1")
        else:
            st.error("Some clues do not match yet. Focus on the vertical asymptote and the position relative to the parent graph.")

# ---------- stage 9 ----------
elif stage == "9. Exit Ticket":
    st.header("9. Exit Ticket")
    st.markdown("Answer individually or as a team summary.")
    e1 = st.text_area("1. How can you recognize an exponential graph?")
    e2 = st.text_area("2. How can you recognize a logarithmic graph?")
    e3 = st.text_area("3. What is the relationship between exponential and logarithmic functions?")
    st.latex(r"(3,8) \text{ lies on } y=2^x")
    e4 = st.selectbox("Which point lies on $y=\\log_2x$?", ["Choose", "(8,3)", "(3,8)", "(-8,3)", "(8,-3)"])
    e5 = st.text_area("One thing I understand better now is...")

    if st.button("Submit exit ticket"):
        if e4 == "(8,3)":
            st.success("Exit ticket submitted. The inverse-coordinate answer is correct: $(8,3)$.")
        else:
            st.warning("Exit ticket recorded. Recheck the inverse-coordinate question before finishing.")

st.divider()
st.caption("Teacher tip: use Streamlit Community Cloud or your institution's server to share one link with the class. LaTeX is rendered with Streamlit's built-in math support.")
