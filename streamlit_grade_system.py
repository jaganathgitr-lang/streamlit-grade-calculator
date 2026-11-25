import re
import streamlit as st

st.set_page_config(page_title="Grade & Calculator", page_icon="🎓", layout="wide")

# --------------------------------------------------------------------------
# SHARED STYLING
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Hide Streamlit's own dev toolbar (Deploy button, "...", running-man
       status) -- purely cosmetic chrome from `streamlit run`, not part
       of the app itself. */
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0;
    }

    .calc-display {
        background-color: #eaf7ff;
        color: #111827;
        font-size: 2.4rem;
        font-family: 'Courier New', monospace;
        text-align: right;
        padding: 20px 22px;
        border-radius: 10px;
        margin-bottom: 14px;
        min-height: 68px;
        overflow-x: auto;
        white-space: nowrap;
        border: 2px solid #38bdf8;
    }

    /* Scoped to .st-key-calc_panel only (via st.container(key="calc_panel")
       below) so this does NOT affect the grade calculator's number_input
       +/- steppers, which was the earlier bug -- an unscoped selector was
       matching every button on the page, inflating those tiny steppers
       to full calculator-button size. */
    .st-key-calc_panel button[data-testid^="stBaseButton"] {
        width: 100% !important;
        height: 72px !important;
        font-size: 1.7rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        margin: 0 !important;
        transition: transform 0.05s ease, background-color 0.15s ease;
    }
    .st-key-calc_panel button[data-testid^="stBaseButton"]:active {
        transform: scale(0.96);
    }
    .st-key-calc_panel button[data-testid="stBaseButton-secondary"] {
        background-color: #1f2937 !important;
        color: #f9fafb !important;
        border: 1px solid #374151 !important;
    }
    .st-key-calc_panel button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #374151 !important;
        border-color: #4b5563 !important;
    }
    .st-key-calc_panel button[data-testid="stBaseButton-primary"] {
        background-color: #f59e0b !important;
        color: #111827 !important;
    }
    .st-key-calc_panel button[data-testid="stBaseButton-primary"]:hover {
        background-color: #fbbf24 !important;
        color: #111827 !important;
    }
    .st-key-calc_panel div[data-testid="stVerticalBlock"] .element-container {
        margin-bottom: 0.4rem !important;
    }

    /* Light card styling for the grade panel -- keeps its own number_input
       stepper buttons at their normal small Streamlit size, just gives
       the section a cleaner, contained look. */
    .st-key-grade_panel {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 24px 28px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns(2, gap="large")

# ==========================================================================
# LEFT COLUMN - GRADE CALCULATOR
# ==========================================================================
with left_col:
    with st.container(key="grade_panel"):
        st.header("🎓 Grade Calculator")
        st.write("Enter a mark between 1 and 100 to see the matching letter grade.")

        def mark_to_grade(mark: float) -> str:
            """Converts a numeric mark into its letter grade (inclusive
            boundaries): 90+ -> A, 80-89 -> B, 70-79 -> C, 60-69 -> D, else E."""
            if mark >= 90:
                return "A"
            elif mark >= 80:
                return "B"
            elif mark >= 70:
                return "C"
            elif mark >= 60:
                return "D"
            else:
                return "E"

        # No min_value/max_value here on purpose: Streamlit's number_input
        # silently clamps out-of-range typed values to the nearest bound
        # when those are set, which means a genuinely negative entry would
        # never actually reach our own validation logic below. Leaving the
        # bounds open lets the user type anything, and we validate it
        # ourselves.
        mark = st.number_input(
            "Enter mark",
            value=None,
            step=0.5,
            format="%g",   # shows 78 as "78" and 78.5 as "78.5" -- no forced ".00"
            placeholder="e.g. 85 or 78.5",
            key="mark_input",
        )

        if mark is None:
            st.warning("⚠️ Please enter a mark to see your grade.")
        elif mark <= 0 or mark > 100:
            st.warning("⚠️ Please enter a valid mark between 1 and 100.")
        else:
            grade = mark_to_grade(mark)
            st.success(f"Mark: **{mark:g}** → Grade: **{grade}**")

# ==========================================================================
# RIGHT COLUMN - ARITHMETIC CALCULATOR
# ==========================================================================
with right_col:
    with st.container(key="calc_panel"):
        st.header("🧮 Calculator")

        if "calc_display" not in st.session_state:
            st.session_state.calc_display = ""

        st.markdown(
            f'<div class="calc-display">{st.session_state.calc_display or "0"}</div>',
            unsafe_allow_html=True,
        )

        # Only digits, ., parentheses, and + - * / are ever allowed into the
        # display string (buttons only ever append these), and this regex
        # is checked again before eval() as a second line of defense so
        # nothing else can ever be evaluated.
        SAFE_EXPRESSION = re.compile(r"^[0-9+\-*/.() ]*$")

        def press(key: str):
            current = st.session_state.calc_display
            if key == "C":
                st.session_state.calc_display = ""
            elif key == "⌫":
                st.session_state.calc_display = current[:-1]
            elif key == "+/-":
                # Simplified whole-expression sign toggle (a real
                # calculator only flips the sign of the last entered
                # number, but that needs a small parser -- this keeps the
                # demo logic simple).
                if current.startswith("-"):
                    st.session_state.calc_display = current[1:]
                elif current:
                    st.session_state.calc_display = "-" + current
            elif key == "%":
                if current and SAFE_EXPRESSION.fullmatch(current):
                    try:
                        result = eval(current, {"__builtins__": {}}, {}) / 100
                        st.session_state.calc_display = str(result)
                    except Exception:
                        st.session_state.calc_display = "Error"
            elif key == "=":
                if current and SAFE_EXPRESSION.fullmatch(current):
                    try:
                        result = eval(current, {"__builtins__": {}}, {})
                        st.session_state.calc_display = str(result)
                    except ZeroDivisionError:
                        st.session_state.calc_display = "Error: ÷ by 0"
                    except Exception:
                        st.session_state.calc_display = "Error"
                else:
                    st.session_state.calc_display = "Error"
            else:
                st.session_state.calc_display = current + key

        # Keys that get the colored "primary" styling (functions/operators),
        # everything else renders as a plain "secondary" digit key --
        # mirrors the function-vs-digit color split of a typical physical
        # calculator.
        PRIMARY_KEYS = {"C", "⌫", "%", "/", "*", "-", "+", "=", "+/-"}

        button_rows = [
            ["C", "⌫", "%", "/"],
            ["7", "8", "9", "*"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["+/-", "0", ".", "="],
        ]

        for row in button_rows:
            cols = st.columns(4, gap="small")
            for col, label in zip(cols, row):
                with col:
                    button_type = "primary" if label in PRIMARY_KEYS else "secondary"
                    st.button(
                        label,
                        key=f"calc_btn_{label}",
                        on_click=press,
                        args=(label,),
                        type=button_type,
                    )