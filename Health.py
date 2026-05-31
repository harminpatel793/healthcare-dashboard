# ===========================================
#                MODULES
# ===========================================


import kagglehub
import pandas as pd
import os
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from groq import Groq

# ==========================================
#        DATA INFO AND CLEANING
# ==========================================

path = kagglehub.dataset_download("prasad22/healthcare-dataset")
    
print("Files:", os.listdir(path))
    
df = pd.read_csv(os.path.join(path, os.listdir(path)[0]))
    
    
df['Name'] = df['Name'].str.strip().str.title()
df['Blood Type'] = df['Blood Type'].str.strip()
df['Medical Condition'] = df['Medical Condition'].str.strip()
df['Admission Type'] = df['Admission Type'].str.strip()
df['Medication'] = df['Medication'].str.strip()
df['Test Results'] = df['Test Results'].str.strip()


print(df['Insurance Provider'].unique())
# ===============================================
#                   STREAMLIT
# ===============================================

st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide"
)


def get_kpi(filtered_df):
    if filtered_df.empty:
        return{
            "total_patients": 0,
            "total_billing_amount": 0,
            "avg_billing_amount": 0
        }
    return {
        "total_patients": f"{len(filtered_df):,}",
        "total_billing_amount": f"${filtered_df['Billing Amount'].sum():,.2f}",
        "avg_billing_amount": f"${filtered_df['Billing Amount'].mean():,.2f}"
    }


def show_kpi(title, value):
    st.markdown(f"""
        <style>
            .kpi-card{{
                background-color: #161a24;
                border: 1px solid #2d3139;
                padding: 30px;
                margin: 15px 0;
                border-radius: 15px;
                box-shadow: 0 0 10px rgba(0, 243, 255, 0.1);
                text-align: center;
                transition: all 0.3s ease;
            }}
            .kpi-card:hover{{
                transform: translateY(-5px);
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.6);
            }}    
            
        </style>
        <div class='kpi-card'>
            <h2 style='color:grey'>{title}</h2>
            <h4 style='color:#F8F8FF'>{value}</h4>
        </div>
    """, unsafe_allow_html=True)


def patient_blood_type(filtered_df):
    st.markdown("<h3>🩸 Blood Count vs Patients</h3>", unsafe_allow_html=True)

    blood_counts = filtered_df['Blood Type'].value_counts().reset_index()
    blood_counts.columns = ['Blood Type', 'Count']

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=blood_counts['Blood Type'],
            y=blood_counts['Count'],
            marker=dict(
                color=['#007ea7', '#00a8cc', '#674f95', '#a14e9a', '#d44c8d', '#f9596f', '#ff7a47', '#ffa600'], 
                line=dict(width=0), 
                cornerradius=8
            ),
            hoverinfo="all",
            hovertemplate='<b>%{x}</b><br>' + "Total Patients" + ': %{y:,.0f}<extra></extra>'
        )
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Blood Types",
        yaxis_title="Total Patients",
        margin=dict(t=20, b=20, l=20, r=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def patient_medical_condition(filtered_df):
    st.markdown("<h3>😷 Number of Patients by Their Medical Condition</h3>", unsafe_allow_html=True)

    Medical_Condition_count = filtered_df['Medical Condition'].value_counts().reset_index()
    Medical_Condition_count.columns = ['Medical Condition', 'Count']

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=Medical_Condition_count['Medical Condition'],
            y=Medical_Condition_count['Count'],
            marker=dict(
                color=['#4823c5', '#af00ac', '#e90086', '#ff185d', '#ff6c35', '#ffa600'],
                line=dict(width=0),
                cornerradius=8
            ),
            hoverinfo='all',
            hovertemplate='<b>%{x}</b><br>' + "Medical Condition" + ': %{y:,.0f}<extra></extra>'
        )
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Medical Condition",
        yaxis_title="Patients",
        margin=dict(t=20, b=20, l=20, r=20)
    )


    st.plotly_chart(fig, use_container_width=True)


def top_10_doc(filtered_df):
    st.markdown("<h3>🧑🏻‍⚕️ Doctors Appointed Per Patient</h3>", unsafe_allow_html=True)

    top_10 = filtered_df['Doctor'].value_counts().head(10).reset_index()
    top_10.columns = ['Doctor', 'Patients']

    
    top_10 = top_10.iloc[::-1]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=top_10['Patients'],
            y=top_10['Doctor'],
            orientation='h',
            marker=dict(color=['#2f355c', '#553e73', '#824280', '#b04480', '#d74b74', '#f45e5d', '#ff7f3d','#ffa600', '#e90086', '#ff185d'], line=dict(width=0), cornerradius=8),
            hoverinfo='all'
        )
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Patients",
        yaxis_title="Doctors",
        margin=dict(t=20, b=20, l=20, r=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def patient_admission_timeline(filtered_df):

    st.markdown("<h3>📈 Dual Axis Chart</h3>", unsafe_allow_html=True)

    # Create a local copy to avoid modifying the original dataframe slice
    timeline_df = filtered_df.copy()

    timeline_df['Date of Admission'] = pd.to_datetime(timeline_df['Date of Admission'])
    timeline_df['month_year'] = timeline_df['Date of Admission'].dt.to_period('M')
    admission_count = timeline_df.groupby('month_year')['Name'].count().reset_index()
    admission_count.columns = ['Month', 'Admissions']
    admission_count['Month'] = admission_count['Month'].astype(str)

    timeline_df['Discharge Date'] = pd.to_datetime(timeline_df['Discharge Date'])
    timeline_df['discharge_month'] = timeline_df['Discharge Date'].dt.to_period('M')
    discharge_count = timeline_df.groupby('discharge_month')['Name'].count().reset_index()
    discharge_count.columns = ['Month', 'Discharges']
    discharge_count['Month'] = discharge_count['Month'].astype(str)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=admission_count['Month'],
            y=admission_count['Admissions'],
            name="Admissions",
            mode="lines+text",
            marker=dict(line=dict(
                width=2,
                color="blue"
            )),
            hoverinfo="all",
            hovertemplate='<b>%{x}</b><br>' + "Total Admitted Patients" + ': %{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=discharge_count['Month'],
            y=discharge_count['Discharges'],
            name="Discharges",
            mode="lines+text",
            marker=dict(
                line=dict(
                    width=2,
                    color="orange"
                )
            ),
            hoverinfo="all",
            hovertemplate='<b>%{x}</b><br>' + "Total Discharged Patients" + ': %{y:,.0f}<extra></extra>'
        ),
        secondary_y=True 
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Timeline",
        yaxis_title="Admissions Discharge of Patients",
        yaxis2_title="Discharge of Patients"
    )

    st.plotly_chart(fig, use_container_width=True)



def admission_type(filtered_df):
    st.markdown("<h3>👥 Admission Type Distribution</h3>", unsafe_allow_html=True)

    patient_count = filtered_df['Admission Type'].value_counts().reset_index()
    patient_count.columns=['Type', 'Count']

    fig=go.Figure()

    fig.add_trace(
        go.Pie(
            labels=patient_count['Type'],
            values=patient_count['Count'],
            name="Admission Type",
            hole=0.4,
            marker=dict(colors=['#00E5FF', '#FF4A5A', '#FFB020'], line=dict(width=2, color='#000000')),
            pull=[0, 0, 0.1],
            textinfo="label+percent",
            textposition="auto"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        annotations=[dict(text="Admission Type", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(color="lightgrey", size=16))]
    )

    st.plotly_chart(fig, use_container_width=True)


def medication_distribution(filtered_df):
    st.markdown("<h3>💊 Medication Distribution</h3>", unsafe_allow_html=True)

    medication_count = filtered_df['Medication'].value_counts().reset_index()
    medication_count.columns=['Medication', 'Count']


    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            labels=medication_count['Medication'],
            values=medication_count['Count'],
            hole=0.4,
            pull=[0.1, 0, 0, 0, 0],
            marker=dict(colors=["#7C4AED", "#00E5FF", "#00E676", "#FFB020", "#FF4A5A"], line=dict(color="#000000", width=2)),
            hoverinfo="label+value"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        annotations=[dict(text="Medication Type", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(color="lightgrey", size=16))]
    )

    st.plotly_chart(fig, use_container_width=True)


def test_result_distribution(filtered_df):
    st.markdown("<h3>📄 Test Results</h3>", unsafe_allow_html=True)

    test_count = filtered_df['Test Results'].value_counts().reset_index()
    test_count.columns=['Test', 'Count']


    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            labels=test_count['Test'],
            values=test_count['Count'],
            hole=0.4,
            pull=[0, 0.1, 0],
            marker=dict(colors=["#FF4A5A", "#00E676", "#FFB020"], line=dict(color="#000000", width=2)),
            hoverinfo="label+value"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        annotations=[dict(text="Test Results", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(color="lightgrey", size=16))]
    )

    st.plotly_chart(fig, use_container_width=True)


def insurance(filtered_df):
    st.markdown("<h3>💵 Insurance Providers</h3>", unsafe_allow_html=True)

    insurance_count = filtered_df['Insurance Provider'].value_counts().reset_index()
    insurance_count.columns=['Insurance_Company', 'Count']

    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            labels=insurance_count['Insurance_Company'],
            values=insurance_count['Count'],
            hole=0.4,
            pull=[0.1, 0, 0, 0, 0],
            marker=dict(colors=["#7C4AED", "#00E5FF", "#00E676", "#FFB020", "#FF4A5A"], line=dict(color="#000000", width=2)),
            hoverinfo="label+value"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        annotations=[dict(text="Insurance", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(color="lightgrey", size=16))]
    )

    st.plotly_chart(fig, use_container_width=True)



def generate_insights(filtered_df):

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    # Data summary to pass to AI
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

    prompt = prompt = f"""
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
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    insights = response.choices[0].message.content

    st.markdown(f"""
        <div style='background-color:#161a24; border:1px solid #2d3139; 
        padding:25px; border-radius:15px; color:#F8F8FF; line-height:1.8; font-size:20px;'>
            {insights}
        </div>
    """, unsafe_allow_html=True)



def main():
    st.markdown("<h1 style='background: #00F3FB;background: linear-gradient(to right, #00F3FB 0%, #33FF2C 100%);-webkit-background-clip: text;-webkit-text-fill-color: transparent;'>Healthcare Analytics Dashboard</h1>", unsafe_allow_html=True)

    st.markdown("<p style='color:grey'>Analyzes Data and Help to Manage Hospital</p>", unsafe_allow_html=True)

    # ===========================    
    # SIDEBAR FILTERS
    # ===========================

    st.sidebar.title("🔍 Filters")


    st.sidebar.markdown("<h4>Select Blood Types</h4>", unsafe_allow_html=True)
    unique_blood_types = df['Blood Type'].unique()
    selected_blood_type = st.sidebar.multiselect("Select Blood Types", options=unique_blood_types, default=unique_blood_types, placeholder='Blood Types', label_visibility="collapsed", key='blood_typ')


    st.sidebar.markdown("<h4>Select Medical Conditions</h4>", unsafe_allow_html=True)
    all_conditions = sorted(df['Medical Condition'].unique())
    selected_conditions = st.sidebar.multiselect("Medical Conditions", options=all_conditions, default=all_conditions, label_visibility='collapsed', key='condition')


    filtered_df = df.copy()

    blood_mask = df['Blood Type'].isin(selected_blood_type)
    condition_mask = df['Medical Condition'].isin(selected_conditions)
    
    # Combine them using & (AND). A row is only kept if BOTH filters say True.
    filtered_df = df[blood_mask & condition_mask]
    

    # ===========================
    # KPI CARDS
    # ===========================

    if filtered_df.empty:
        st.warning("⚠️ No data matches the selected filter combinations. Try adjusting your sidebar filters!")

    else:
        kpi = get_kpi(filtered_df)

        col1, col2, col3 = st.columns(3)

        with col1:
            show_kpi("Total Patients", kpi['total_patients'])

        with col2:
            show_kpi("Total Billing Amount", kpi['total_billing_amount'])

        with col3:
            show_kpi("Average Billing Amount", kpi['avg_billing_amount'])

        st.divider()


        # ===============================    
        # BAR CHARTS
        # ===============================


        col1, col2 = st.columns(2)

        with col1:
            patient_blood_type(filtered_df)

        with col2:
            patient_medical_condition(filtered_df)


        patient_admission_timeline(filtered_df)

        st.divider()

        top_10_doc(filtered_df)

        # ================================            
        # DONUT CHARTS
        # ================================    

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


        

        # ===================================      
        # AI INSIGHTS AND RECOMMENDATIONS
        # ===================================

        st.markdown("<h3>🤖 AI Insights & Recommendations</h3>", unsafe_allow_html=True)

        insights = st.button("💡 Generate Insights")

        if insights:
            with st.spinner("Generating Insights..."):
                generate_insights(filtered_df)
            

if __name__ == "__main__":
    main()