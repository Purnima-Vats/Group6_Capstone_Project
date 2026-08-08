"""
Student Course Completion — Executive Dashboard
Run with: streamlit run dashboard_app.py
Expects clean_student_data.csv in ../data/processed/ (default) or the same folder.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Student Completion Dashboard",
    page_icon="📊",
    layout="wide",
)

ORANGE = "#ea580c"
DARK = "#1f2937"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    candidate_paths = [
        "../data/processed/clean_student_data.csv",
        "data/processed/clean_student_data.csv",
        "clean_student_data.csv",
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            df = pd.read_csv(path, parse_dates=["Enrollment_Date"])
            return df
    return None


df = load_data()

if df is None:
    st.error(
        "Couldn't find `clean_student_data.csv`. Place it in `data/processed/` "
        "(relative to the repo root) or in the same folder as this script, "
        "then reload the page."
    )
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.title("Filters")
st.sidebar.caption("All charts and KPIs below react to these filters.")

all_categories = sorted(df["Category"].unique())
all_levels = sorted(df["Course_Level"].unique())
all_employment = sorted(df["Employment_Status"].unique())
all_payment = sorted(df["Payment_Mode"].unique())
all_device = sorted(df["Device_Type"].unique())
all_tiers = sorted(df["engagement_tier"].dropna().unique())
all_months = sorted(df["Enrollment_Date"].dt.to_period("M").astype(str).unique())
full_month_range = (all_months[0], all_months[-1])


def apply_preset(categories=None, levels=None, employment=None, payment=None,
                  device=None, tiers=None, dates=None):
    """Jump straight to a common view instead of manually deselecting options one by one."""
    st.session_state["f_category"] = categories if categories is not None else all_categories
    st.session_state["f_level"] = levels if levels is not None else all_levels
    st.session_state["f_employment"] = employment if employment is not None else all_employment
    st.session_state["f_payment"] = payment if payment is not None else all_payment
    st.session_state["f_device"] = device if device is not None else all_device
    st.session_state["f_tier"] = tiers if tiers is not None else all_tiers
    st.session_state["f_daterange"] = dates if dates is not None else full_month_range
    st.rerun()


# Initialize session state once, up front, instead of passing default= on every widget
# creation below (passing both default= and a session-state-backed key= triggers a
# Streamlit warning since it's ambiguous which one should win).
st.session_state.setdefault("f_category", all_categories)
st.session_state.setdefault("f_level", all_levels)
st.session_state.setdefault("f_employment", all_employment)
st.session_state.setdefault("f_payment", all_payment)
st.session_state.setdefault("f_device", all_device)
st.session_state.setdefault("f_tier", all_tiers)
st.session_state.setdefault("f_daterange", full_month_range)


st.sidebar.subheader("Quick presets")
p1, p2 = st.sidebar.columns(2)
if p1.button("At-Risk", width='stretch', help="Engagement Tier = Low"):
    apply_preset(tiers=["Low"])
if p2.button("Free-Tier", width='stretch', help="Payment Mode = Free"):
    apply_preset(payment=["Free"])
if st.sidebar.button("Reset all filters", width='stretch'):
    apply_preset()

# Immediate feedback on what's currently active, no need to scroll down to check
active_bits = []
if set(st.session_state.get("f_tier", all_tiers)) != set(all_tiers):
    active_bits.append(f"Tier: {', '.join(st.session_state['f_tier'])}")
if set(st.session_state.get("f_payment", all_payment)) != set(all_payment):
    active_bits.append(f"Payment: {', '.join(st.session_state['f_payment'])}")
if set(st.session_state.get("f_category", all_categories)) != set(all_categories):
    active_bits.append(f"Category: {', '.join(st.session_state['f_category'])}")
if set(st.session_state.get("f_level", all_levels)) != set(all_levels):
    active_bits.append(f"Level: {', '.join(st.session_state['f_level'])}")
if set(st.session_state.get("f_employment", all_employment)) != set(all_employment):
    active_bits.append(f"Employment: {', '.join(st.session_state['f_employment'])}")
if set(st.session_state.get("f_device", all_device)) != set(all_device):
    active_bits.append(f"Device: {', '.join(st.session_state['f_device'])}")

if active_bits:
    st.sidebar.success("🔎 Active: " + " · ".join(active_bits))
else:
    st.sidebar.caption("No filters active — showing all students.")

st.sidebar.divider()

def multiselect_all(label, options, key):
    options = sorted(options)
    return st.sidebar.multiselect(label, options, key=key)

categories = multiselect_all("Category", df["Category"].unique(), key="f_category")
payment_mode = multiselect_all("Payment_Mode", df["Payment_Mode"].unique(), key="f_payment")

# Small, fixed option sets get one-click pill toggles instead of a dropdown
st.sidebar.markdown("**Course Level**")
levels = st.sidebar.pills(
    "Course_Level", all_levels, selection_mode="multi",
    key="f_level", label_visibility="collapsed",
)

st.sidebar.markdown("**Engagement Tier**")
engagement_tier = st.sidebar.pills(
    "Engagement Tier", all_tiers, selection_mode="multi",
    key="f_tier", label_visibility="collapsed",
)

st.sidebar.markdown("**Employment Status**")
employment = st.sidebar.pills(
    "Employment_Status", all_employment, selection_mode="multi",
    key="f_employment", label_visibility="collapsed",
)

st.sidebar.markdown("**Device Type**")
device = st.sidebar.pills(
    "Device_Type", all_device, selection_mode="multi",
    key="f_device", label_visibility="collapsed",
)

start_month, end_month = st.sidebar.select_slider(
    "Enrollment month range",
    options=all_months,
    value=full_month_range,
    key="f_daterange",
)

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
mask = (
    df["Category"].isin(categories)
    & df["Course_Level"].isin(levels)
    & df["Employment_Status"].isin(employment)
    & df["Payment_Mode"].isin(payment_mode)
    & df["Device_Type"].isin(device)
    & df["engagement_tier"].isin(engagement_tier)
)

df_month = df["Enrollment_Date"].dt.to_period("M").astype(str)
mask &= (df_month >= start_month) & (df_month <= end_month)

filtered_df = df[mask]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("📊 Student Course Completion Dashboard")
st.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} students based on the current filters."
)

if len(filtered_df) == 0:
    st.warning("No students match the current filter selection. Try widening a filter.")
    st.stop()

# ---------------------------------------------------------------------------
# KPI row (styled as cards)
# ---------------------------------------------------------------------------
overall_completion = df["completed_flag"].mean() * 100
filtered_completion = filtered_df["completed_flag"].mean() * 100
at_risk_count = (filtered_df["engagement_tier"] == "Low").sum()
avg_engagement = filtered_df["engagement_score"].mean()

st.markdown(
    """
    <style>
    .kpi-card {
        background-color: #fff7ed;
        border: 1px solid #fde3c9;
        border-radius: 10px;
        padding: 14px 16px;
        height: 122px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
    }
    .kpi-label {
        color: #6b7280;
        font-size: 14px;
    }
    .kpi-value {
        color: #1f2937;
        font-size: 32px;
        font-weight: 600;
        line-height: 1.2;
    }
    .kpi-delta {
        font-size: 12.5px;
        font-weight: 600;
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        width: fit-content;
    }
    .kpi-delta.positive { color: #15803d; background-color: #dcfce7; }
    .kpi-delta.negative { color: #b91c1c; background-color: #fee2e2; }
    .kpi-delta.neutral { color: #6b7280; background-color: #f3f4f6; }
    </style>
    """,
    unsafe_allow_html=True,
)

def kpi_card(label, value, delta_text=None, delta_direction="neutral"):
    if delta_text:
        delta_html = f'<div class="kpi-delta {delta_direction}">{delta_text}</div>'
    else:
        delta_html = '<div class="kpi-delta neutral" style="visibility:hidden;">placeholder</div>'
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

completion_delta = filtered_completion - overall_completion
if abs(completion_delta) < 0.05:
    delta_text, delta_dir = "＝ same as overall", "neutral"
elif completion_delta > 0:
    delta_text, delta_dir = f"↑ +{completion_delta:.1f} pts vs overall", "positive"
else:
    delta_text, delta_dir = f"↓ {completion_delta:.1f} pts vs overall", "negative"

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Completion Rate", f"{filtered_completion:.1f}%", delta_text, delta_dir)
with k2:
    kpi_card("Total Students", f"{len(filtered_df):,}")
with k3:
    kpi_card("Avg. Engagement Score", f"{avg_engagement:.1f} / 100")
with k4:
    kpi_card("At-Risk Students (Low engagement)", f"{at_risk_count:,}")

st.divider()

# ---------------------------------------------------------------------------
# Completion rate by Engagement Tier — the strongest single finding in the EDA
# ---------------------------------------------------------------------------
st.subheader("Completion Rate by Engagement Tier")
st.caption("The largest gap found anywhere in the analysis: High vs Low engagement students, "
           "an 18.5 point difference at full scale.")
tier_order = ["Low", "Medium", "High"]
tier_rate = (
    filtered_df.groupby("engagement_tier", observed=True)["completed_flag"]
    .mean().mul(100).reindex(tier_order)
)
fig = px.bar(
    tier_rate, x=tier_rate.index, y=tier_rate.values,
    labels={"x": "Engagement Tier", "y": "Completion Rate (%)"},
    color=tier_rate.index,
    color_discrete_map={"Low": "#fca5a5", "Medium": "#fdba74", "High": ORANGE},
)
fig.add_hline(y=overall_completion, line_dash="dash", line_color=DARK, annotation_text="Overall avg")
fig.update_layout(showlegend=False)
st.plotly_chart(fig)

st.divider()

# ---------------------------------------------------------------------------
# Completion rate by Category / Course_Level
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Completion Rate by Category")
    cat_rate = (
        filtered_df.groupby("Category")["completed_flag"].mean().mul(100).sort_values(ascending=False)
    )
    fig = px.bar(
        cat_rate, x=cat_rate.index, y=cat_rate.values,
        labels={"x": "Category", "y": "Completion Rate (%)"},
        color_discrete_sequence=[ORANGE],
    )
    fig.add_hline(y=overall_completion, line_dash="dash", line_color=DARK,
                   annotation_text="Overall avg")
    st.plotly_chart(fig)

with c2:
    st.subheader("Completion Rate by Course Level")
    level_rate = (
        filtered_df.groupby("Course_Level")["completed_flag"].mean().mul(100).sort_values(ascending=False)
    )
    fig = px.bar(
        level_rate, x=level_rate.index, y=level_rate.values,
        labels={"x": "Course Level", "y": "Completion Rate (%)"},
        color_discrete_sequence=[DARK],
    )
    fig.add_hline(y=overall_completion, line_dash="dash", line_color=ORANGE,
                   annotation_text="Overall avg")
    st.plotly_chart(fig)

# ---------------------------------------------------------------------------
# Completion rate by Payment Mode (the strongest structural finding)
# ---------------------------------------------------------------------------
st.subheader("Completion Rate by Payment Mode")
st.caption("The largest structural gap found in the EDA lives here — Free enrollments complete "
           "at a noticeably lower rate than paid ones.")
pay_rate = (
    filtered_df.groupby("Payment_Mode")["completed_flag"].mean().mul(100).sort_values(ascending=False)
)
fig = px.bar(
    pay_rate, x=pay_rate.index, y=pay_rate.values,
    labels={"x": "Payment Mode", "y": "Completion Rate (%)"},
    color=pay_rate.values,
    color_continuous_scale=["#fca5a5", ORANGE],
)
fig.add_hline(y=overall_completion, line_dash="dash", line_color=DARK, annotation_text="Overall avg")
fig.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig)

st.divider()

# ---------------------------------------------------------------------------
# Performance comparison
# ---------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Video Completion Rate by Status")
    fig = px.box(
        filtered_df, x="Completed", y="Video_Completion_Rate",
        color="Completed", color_discrete_map={"Completed": ORANGE, "Not Completed": DARK},
    )
    st.plotly_chart(fig)

with c4:
    st.subheader("Time Spent (Hours) by Status")
    fig = px.box(
        filtered_df, x="Completed", y="Time_Spent_Hours",
        color="Completed", color_discrete_map={"Completed": ORANGE, "Not Completed": DARK},
    )
    st.plotly_chart(fig)

# ---------------------------------------------------------------------------
# Trend over time
# ---------------------------------------------------------------------------
st.subheader("Enrollment and Completion Trend")
monthly = (
    filtered_df.groupby(filtered_df["Enrollment_Date"].dt.to_period("M").astype(str))
    .agg(enrollments=("Student_ID", "count"), completion_rate=("completed_flag", "mean"))
    .reset_index()
    .rename(columns={"Enrollment_Date": "month"})
)
monthly["completion_rate"] *= 100
monthly = monthly.sort_values("month")

if len(monthly) > 1:
    fig = px.line(
        monthly, x="month", y="completion_rate", markers=True,
        labels={"month": "Enrollment Month", "completion_rate": "Completion Rate (%)"},
        color_discrete_sequence=[ORANGE],
    )
    st.plotly_chart(fig)
else:
    st.info("Widen the date range filter to see a trend over more than one month.")

st.divider()

# ---------------------------------------------------------------------------
# Drill-down table
# ---------------------------------------------------------------------------
st.subheader("Student Drill-Down")
st.caption("Filtered student list. Name is excluded for privacy, Student_ID is kept as the reference.")

display_cols = [
    "Student_ID", "Category", "Course_Level", "Employment_Status", "Payment_Mode",
    "Device_Type", "engagement_tier", "engagement_score", "performance_score",
    "Progress_Percentage", "Completed",
]
display_cols = [c for c in display_cols if c in filtered_df.columns]

st.dataframe(
    filtered_df[display_cols].sort_values("engagement_score", ascending=True),
    height=400,
)

st.caption(
    "Built for the Data Analysis Capstone Project — Student Course Completion Prediction dataset."
)