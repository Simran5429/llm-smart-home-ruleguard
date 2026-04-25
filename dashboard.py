import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from llm.generator import generate_rule
from validator.checker import validate_rule, check_intent_mismatch, suggest_alternative
from simulator.home_state import load_smart_home_state

st.set_page_config(layout="wide")
st.title("Dashboard")

data = load_smart_home_state()

# ---------- SESSION STATE ----------
if "valid_count" not in st.session_state:
    st.session_state.valid_count = 0
if "invalid_count" not in st.session_state:
    st.session_state.invalid_count = 0
if "mismatch_count" not in st.session_state:
    st.session_state.mismatch_count = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "counted_requests" not in st.session_state:
    st.session_state.counted_requests = []

# store latest run results
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = None
if "last_rule" not in st.session_state:
    st.session_state.last_rule = None
if "last_validation" not in st.session_state:
    st.session_state.last_validation = None
if "last_mismatch" not in st.session_state:
    st.session_state.last_mismatch = None

# ---------- HELPERS ----------
def show_result_box(title, status, reason, success_text, fail_text):
    if status:
        st.markdown(
            f"""
            <div style="padding:15px; border-radius:10px; background-color:#d4edda; color:#155724; border:1px solid #c3e6cb; margin-bottom:10px;">
                <h4 style="margin:0 0 8px 0;">{title}</h4>
                <p style="margin:0;"><strong>{success_text}</strong></p>
                <p style="margin:6px 0 0 0;">Reason: {reason}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="padding:15px; border-radius:10px; background-color:#f8d7da; color:#721c24; border:1px solid #f5c6cb; margin-bottom:10px;">
                <h4 style="margin:0 0 8px 0;">{title}</h4>
                <p style="margin:0;"><strong>{fail_text}</strong></p>
                <p style="margin:6px 0 0 0;">Reason: {reason}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------- TOP METRICS ----------
st.subheader("Statistics")
col_stats, col_chart = st.columns([1, 1])

with col_stats:
    st.metric("Valid Rules", st.session_state.valid_count)
    st.metric("Invalid Rules", st.session_state.invalid_count)
    st.metric("Intent Mismatches", st.session_state.mismatch_count)

with col_chart:
    chart_data = pd.DataFrame({
        "Category": ["Valid", "Invalid", "Mismatch"],
        "Count": [
            st.session_state.valid_count,
            st.session_state.invalid_count,
            st.session_state.mismatch_count
        ]
    })

    fig, ax = plt.subplots(figsize=(3, 2))
    ax.bar(chart_data["Category"], chart_data["Count"])
    ax.set_title("Summary", fontsize=9)
    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    plt.tight_layout()
    st.pyplot(fig)

st.divider()

# ---------- MAIN LAYOUT ----------
col1, col2 = st.columns([1, 2])

# ---------- LEFT SIDE ----------
with col1:
    st.subheader("Rule Input")
    user_input = st.text_input("Enter command:")

    if st.button("Run Rule"):
        if user_input.strip():
            rule = generate_rule(user_input, data)
            result = validate_rule(rule, data)
            mismatch_result = check_intent_mismatch(user_input, rule)

            # save latest run
            st.session_state.last_user_input = user_input
            st.session_state.last_rule = rule
            st.session_state.last_validation = result
            st.session_state.last_mismatch = mismatch_result

            # save history
            st.session_state.history.append({
                "Request": user_input,
                "Generated Rule": json.dumps(rule),
                "Valid": result["valid"],
                "Validation Reason": result["reason"],
                "Intent Mismatch": mismatch_result["mismatch"],
                "Intent Reason": mismatch_result["reason"]
            })

            # count only unique requests
            if user_input not in st.session_state.counted_requests:
                st.session_state.counted_requests.append(user_input)

                if result["valid"]:
                    st.session_state.valid_count += 1
                else:
                    st.session_state.invalid_count += 1

                if mismatch_result["mismatch"]:
                    st.session_state.mismatch_count += 1
            else:
                st.warning("This request was already counted before, so statistics were not increased.")

            st.rerun()
        else:
            st.warning("Please enter a command.")

    if st.button("Reset Dashboard"):
        st.session_state.valid_count = 0
        st.session_state.invalid_count = 0
        st.session_state.mismatch_count = 0
        st.session_state.history = []
        st.session_state.counted_requests = []
        st.session_state.last_user_input = None
        st.session_state.last_rule = None
        st.session_state.last_validation = None
        st.session_state.last_mismatch = None
        st.rerun()

    # show latest result after rerun
    if st.session_state.last_user_input is not None:
        st.write("User Input:", st.session_state.last_user_input)

        st.subheader("Generated Rule")
        st.json(st.session_state.last_rule)

        st.subheader("Validation Result")
        show_result_box(
            title="Validation Check",
            status=st.session_state.last_validation["valid"],
            reason=st.session_state.last_validation["reason"],
            success_text="Rule is structurally valid",
            fail_text="Rule is structurally invalid"
        )

        st.subheader("Intent Check Result")
        show_result_box(
            title="Intent Mismatch Check",
            status=not st.session_state.last_mismatch["mismatch"],
            reason=st.session_state.last_mismatch["reason"],
            success_text="Intent matches the user request",
            fail_text="Intent mismatch detected"
        )


if st.session_state.last_validation is not None:
    if not st.session_state.last_validation["valid"]:
        suggestion = suggest_alternative(st.session_state.last_rule, data)

        if suggestion:
            st.info(f" Suggestion: {suggestion}")



# ---------- RIGHT SIDE ----------
with col2:
    st.subheader("Available Devices and Sensors by Room")

    rooms = data.get("rooms", {})

    with st.container(height=300, border=True):
        for room_name, room_data in rooms.items():
            devices = ", ".join(room_data.get("devices", {}).keys())
            sensors = ", ".join(room_data.get("sensors", {}).keys())

            st.markdown(f"**{room_name.replace('_', ' ').title()}**")
            st.write(f"Devices: {devices}")
            st.write(f"Sensors: {sensors}")
            st.divider()

    st.subheader("Request History Table")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No requests submitted yet.")