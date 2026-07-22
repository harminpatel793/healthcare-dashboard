# ===========================================
#                MODULES
# ===========================================

import os
import kagglehub
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from groq import Groq

# ===========================================
#            COLOR SYSTEM (single source of truth)
# ===========================================
# Cohesive cool-tone ramp (cyan -> blue -> violet -> magenta) used for ALL
# categorical charts. No warm colors here on purpose — orange/red are
# reserved for semantic "warning" states only, so they still mean something
# when they show up.
COOL_RAMP = ["#00E5FF", "#2FB8E8", "#5B8DEF", "#7C6CEF",
             "#9B5CE0", "#C24EC7", "#E14FAE", "#FF4FA0"]

GOOD = "#2ECC71"     # positive / normal / delivered-style states
NEUTRAL = "#F5A623"  # in-progress / pending-style states
BAD = "#FF5A5F"      # negative / abnormal / cancelled-style states

BG_CARD = "#161a24"
BORDER = "#2d3139"
TEXT_MUTED = "#9aa1ad"
TEXT_MAIN = "#F8F8FF"
ACCENT = "#00E5FF"

PLOTLY_LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_MAIN, family="Segoe UI, sans-serif"),
    margin=dict(t=30, b=30, l=30, r=30),
    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
)


# ===========================================
#        DATA LOADING AND CLEANING (cached)
# ===========================================

@st.cache_data(ttl=3600, show_spinner="Loading hospital dataset...")
def load_data():
    if "KAGGLE_USERNAME" in st.secrets:
        os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
        os.environ["KAGGLE_KEY"] = st.secrets["KAGGLE_KEY"]

    path = kagglehub.dataset_download("prasad22/healthcare-dataset")
    data = pd.read_csv(os.path.join(path, os.listdir(path)[0]))

    data['Name'] = data['Name'].str.strip().str.title()
    data['Blood Type'] = data['Blood Type'].str.strip()
    data['Medical Condition'] = data['Medical Condition'].str.strip()
    data['Admission Type'] = data['Admission Type'].str.strip()
    data['Medication'] = data['Medication'].str.strip()
    data['Test Results'] = data['Test Results'].str.strip()
    data['Date of Admission'] = pd.to_datetime(data['Date of Admission'])
    data['Discharge Date'] = pd.to_datetime(data['Discharge Date'])

    return data


# ===============================================
#                   STREAMLIT CONFIG
# ===============================================

st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide"
)

st.markdown(f"""
    <style>
        .kpi-card {{
            background-color: {BG_CARD} !important;
            border: 1px solid {BORDER} !important;
            padding: 22px 20px !important;
            margin: 8px 0 !important;
            border-radius: 14px !important;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.08) !important;
            text-align: center !important;
            transition: all 0.25s ease !important;
            min-height: 130px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }}
        .kpi-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 0 18px rgba(0, 229, 255, 0.35) !important;
            border-color: {ACCENT} !important;
        }}
        .kpi-icon {{
            font-size: 20px !important;
            margin-bottom: 4px !important;
        }}
        .kpi-label {{
            color: {TEXT_MUTED} !important;
            font-family: 'Segoe UI', sans-serif !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            letter-spacing: 0.6px !important;
            text-transform: uppercase !important;
            margin: 0 0 6px 0 !important;
        }}
        .kpi-value {{
            color: {TEXT_MAIN} !important;
            font-family: 'Segoe UI', sans-serif !important;
            font-size: 28px !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
            margin: 0 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        .kpi-sub {{
            color: {TEXT_MUTED} !important;
            font-family: 'Segoe UI', sans-serif !important;
            font-size: 11px !important;
            font-weight: 400 !important;
            margin: 4px 0 0 0 !important;
        }}
        section[data-testid="stSidebar"] h4 {{
            color: {TEXT_MAIN};
            margin-bottom: 4px;
        }}
    </style>
""", unsafe_allow_html=True)


# ===========================================
#              KPI HELPERS
# ===========================================

def get_kpi(filtered_df, full_df):
    if filtered_df.empty:
        return {
            "total_patients": "0",
            "pct_of_total": "0%",
            "total_billing_amount": "$0",
            "avg_billing_amount": "$0",
            "top_condition": "—"
        }

    pct = len(filtered_df) / len(full_df) * 100
    return {
        "total_patients": f"{len(filtered_df):,}",
        "pct_of_total": f"{pct:.1f}% of all patients",
        "total_billing_amount": f"${filtered_df['Billing Amount'].sum():,.0f}",
        "avg_billing_amount": f"${filtered_df['Billing Amount'].mean():,.2f}",
        "top_condition": filtered_df['Medical Condition'].value_counts().index[0]
    }


def show_kpi(icon, label, value, sub=None):
    sub_html = f"<div class='kpi-sub'>{sub}</div>" if sub else ""
    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-icon'>{icon}</div>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value'>{value}</div>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)


# ===========================================
#              CHART FUNCTIONS
# ===========================================

def patient_blood_type(filtered_df):
    st.markdown("<h3>🩸 Blood Count vs Patients</h3>", unsafe_allow_html=True)

    blood_counts = filtered_df['Blood Type'].value_counts().reset_index()
    blood_counts.columns = ['Blood Type', 'Count']

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=blood_counts['Blood Type'],
            y=blood_counts['Count'],
            marker=dict(color=COOL_RAMP, line=dict(width=0), cornerradius=8),
            text=blood_counts['Count'],
            texttemplate="%{text:,}",
            textposition="outside",
            hovertemplate='<b>%{x}</b><br>Total Patients: %{y:,.0f}<extra></extra>'
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        xaxis_title="Blood Type",
        yaxis_title="Total Patients",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def patient_medical_condition(filtered_df):
    st.markdown("<h3>😷 Number of Patients by Medical Condition</h3>", unsafe_allow_html=True)

    condition_count = filtered_df['Medical Condition'].value_counts().reset_index()
    condition_count.columns = ['Medical Condition', 'Count']

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=condition_count['Medical Condition'],
            y=condition_count['Count'],
            marker=dict(color=COOL_RAMP, line=dict(width=0), cornerradius=8),
            text=condition_count['Count'],
            texttemplate="%{text:,}",
            textposition="outside",
            hovertemplate='<b>%{x}</b><br>Patients: %{y:,.0f}<extra></extra>'
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        xaxis_title="Medical Condition",
        yaxis_title="Patients",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def top_10_doc(filtered_df):
    st.markdown("<h3>🧑🏻‍⚕️ Top 10 Doctors by Patient Load</h3>", unsafe_allow_html=True)

    top_10 = filtered_df['Doctor'].value_counts().head(10).reset_index()
    top_10.columns = ['Doctor', 'Patients']
    top_10 = top_10.iloc[::-1]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=top_10['Patients'],
            y=top_10['Doctor'],
            orientation='h',
            marker=dict(color=COOL_RAMP + COOL_RAMP[:2], line=dict(width=0), cornerradius=8),
            text=top_10['Patients'],
            texttemplate="%{text}",
            textposition="outside",
            hovertemplate='<b>%{y}</b><br>Patients: %{x}<extra></extra>'
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        xaxis_title="Patients",
        yaxis_title="",
        showlegend=False,
        height=420
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Note: differences between doctors here are naturally small in this dataset — "
               "treat this as a workload snapshot, not a major variance signal.")


def patient_admission_timeline(filtered_df):
    st.markdown("<h3>📈 Admissions vs Discharges Over Time</h3>", unsafe_allow_html=True)

    timeline_df = filtered_df.copy()
    timeline_df['month_year'] = timeline_df['Date of Admission'].dt.to_period('M')
    admission_count = timeline_df.groupby('month_year')['Name'].count().reset_index()
    admission_count.columns = ['Month', 'Admissions']
    admission_count['Month'] = admission_count['Month'].astype(str)

    timeline_df['discharge_month'] = timeline_df['Discharge Date'].dt.to_period('M')
    discharge_count = timeline_df.groupby('discharge_month')['Name'].count().reset_index()
    discharge_count.columns = ['Month', 'Discharges']
    discharge_count['Month'] = discharge_count['Month'].astype(str)

    def drop_partial_tail(series_df, col):
        if len(series_df) > 2 and series_df[col].iloc[-1] < series_df[col].iloc[:-1].mean() * 0.5:
            return series_df.iloc[:-1]
        return series_df

    admission_count = drop_partial_tail(admission_count, 'Admissions')
    discharge_count = drop_partial_tail(discharge_count, 'Discharges')

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=admission_count['Month'], y=admission_count['Admissions'],
            name="Admissions", mode="lines+markers",
            line=dict(color=COOL_RAMP[0], width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{x}</b><br>Admissions: %{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=discharge_count['Month'], y=discharge_count['Discharges'],
            name="Discharges", mode="lines+markers",
            line=dict(color=COOL_RAMP[6], width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{x}</b><br>Discharges: %{y:,.0f}<extra></extra>'
        ),
        secondary_y=True
    )

    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        xaxis_title="Timeline",
        yaxis_title="Admissions",
        yaxis2_title="Discharges",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)


def _donut(filtered_df, column, title, colors, emoji, center_label):
    st.markdown(f"<h3>{emoji} {title}</h3>", unsafe_allow_html=True)

    counts = filtered_df[column].value_counts().reset_index()
    counts.columns = ['Label', 'Count']
    total = counts['Count'].sum()

    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=counts['Label'],
            values=counts['Count'],
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#0e1117", width=2)),
            textinfo="percent",
            hovertemplate='<b>%{label}</b><br>%{value:,} patients<extra></extra>'
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        annotations=[dict(
            text=f"<b>{total:,}</b><br><span style='font-size:12px;color:{TEXT_MUTED}'>{center_label}</span>",
            x=0.5, y=0.5, showarrow=False, font=dict(size=20, color=TEXT_MAIN)
        )]
    )
    st.plotly_chart(fig, use_container_width=True)


def admission_type(filtered_df):
    # Semantic colors here on purpose: Emergency = warning red, Elective = calm blue, Urgent = amber
    _donut(filtered_df, 'Admission Type', "Admission Type Distribution",
           [BAD, COOL_RAMP[0], NEUTRAL], "👥", "patients")


def medication_distribution(filtered_df):
    _donut(filtered_df, 'Medication', "Medication Distribution",
           COOL_RAMP, "💊", "prescriptions")


def test_result_distribution(filtered_df):
    # Semantic: Abnormal = red, Normal = green, Inconclusive = amber
    _donut(filtered_df, 'Test Results', "Test Results",
           [BAD, GOOD, NEUTRAL], "📄", "results")


def insurance(filtered_df):
    _donut(filtered_df, 'Insurance Provider', "Insurance Providers",
           COOL_RAMP, "💵", "patients")


# ===========================================
#            AI INSIGHTS
# ===========================================

def generate_insights(filtered_df):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    summary = f"""
    Total Patients: {len(filtered_df)}
    Average Billing Amount: ${filtered_df['Billing Amount'].mean():,.2f}
    Total Billing Amount: ${filtered_df['Billing Amount'].sum():,.2f}
    Most Common Blood Type: {filtered_df['Blood Type'].value_counts().index[0]}
    Most Common Medical Condition: {filtered_df['Medical Condition'].value_counts().index[0]}
    Most Common Medication: {filtered_df['Medication'].value_counts().index[0]}
    Most Common Admission Type: {filtered_df['Admission Type'].value_counts().index[0]}
    Test Results Distribution: {filtered_df['Test Results'].value_counts().to_dict()}
    """

    prompt = f"""
    You are a senior healthcare business analyst.

    Analyze the dataset and respond in STRICT structured HTML format.

    Rules:
    - No introduction or explanation
    - Be sharp, data-driven, and executive level
    - Avoid generic statements

    Structure EXACTLY like this:

    <b>📊 Key Insights</b>
    <ul>
    <li>Insight 1 (specific + numbers if possible)</li>
    <li>Insight 2</li>
    <li>Insight 3</li>
    </ul>
    <br>
    <b>⚠️ Risks / Concerns</b>
    <ul>
    <li>Risk 1</li>
    <li>Risk 2</li>
    </ul>
    <br>
    <b>💡 Recommendations</b>
    <ul>
    <li>Actionable step 1</li>
    <li>Actionable step 2</li>
    <li>Actionable step 3</li>
    </ul>

    Data:
    {summary}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    insights = response.choices[0].message.content

    st.markdown(f"""
        <div style='background-color:{BG_CARD}; border:1px solid {BORDER};
        padding:25px; border-radius:15px; color:{TEXT_MAIN}; line-height:1.8; font-size:18px;'>
            {insights}
        </div>
    """, unsafe_allow_html=True)


# ===========================================
#                    MAIN
# ===========================================

def main():
    df = load_data()

    st.markdown(
        "<h1 style='background: linear-gradient(to right, #00E5FF 0%, #7C6CEF 100%);"
        "-webkit-background-clip: text;-webkit-text-fill-color: transparent;'>"
        "Healthcare Analytics Dashboard</h1>", unsafe_allow_html=True
    )
    st.markdown(f"<p style='color:{TEXT_MUTED}'>Analyzes hospital data to support operational decisions</p>",
                unsafe_allow_html=True)

    # ===========================
    # SIDEBAR FILTERS
    # ===========================
    st.sidebar.title("🔍 Filters")

    st.sidebar.markdown("<h4>Blood Types</h4>", unsafe_allow_html=True)
    unique_blood_types = sorted(df['Blood Type'].unique())
    selected_blood_type = st.sidebar.multiselect(
        "Select Blood Types", options=unique_blood_types, default=unique_blood_types,
        label_visibility="collapsed", key='blood_typ'
    )

    st.sidebar.markdown("<h4>Medical Conditions</h4>", unsafe_allow_html=True)
    all_conditions = sorted(df['Medical Condition'].unique())
    selected_conditions = st.sidebar.multiselect(
        "Medical Conditions", options=all_conditions, default=all_conditions,
        label_visibility='collapsed', key='condition'
    )

    if selected_blood_type and selected_conditions:
        st.sidebar.caption(f"Showing **{len(selected_blood_type)}** blood type(s), "
                            f"**{len(selected_conditions)}** condition(s)")

    blood_mask = df['Blood Type'].isin(selected_blood_type)
    condition_mask = df['Medical Condition'].isin(selected_conditions)
    filtered_df = df[blood_mask & condition_mask]

    # ===========================
    # KPI CARDS
    # ===========================
    if filtered_df.empty:
        st.warning("⚠️ No data matches the selected filter combinations. Try adjusting your sidebar filters!")
        return

    kpi = get_kpi(filtered_df, df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_kpi("🧑‍🤝‍🧑", "Total Patients", kpi['total_patients'])
    with col2:
        show_kpi("💰", "Total Billing", kpi['total_billing_amount'])
    with col3:
        show_kpi("📊", "Avg Billing / Patient", kpi['avg_billing_amount'])
    with col4:
        show_kpi("🎯", "Top Condition", kpi['top_condition'])

    st.divider()

    # ===========================
    # BAR CHARTS
    # ===========================
    col1, col2 = st.columns(2)
    with col1:
        patient_blood_type(filtered_df)
    with col2:
        patient_medical_condition(filtered_df)

    patient_admission_timeline(filtered_df)
    st.divider()
    top_10_doc(filtered_df)

    # ===========================
    # DONUT CHARTS
    # ===========================
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        admission_type(filtered_df)
    with col2:
        medication_distribution(filtered_df)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        test_result_distribution(filtered_df)
    with col2:
        insurance(filtered_df)

    st.divider()

    # ===========================
    # AI INSIGHTS
    # ===========================
    st.markdown("<h3>🤖 AI Insights & Recommendations</h3>", unsafe_allow_html=True)
    if st.button("💡 Generate Insights"):
        with st.spinner("Generating Insights..."):
            generate_insights(filtered_df)


if __name__ == "__main__":
    main()