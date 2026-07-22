# 🏥 Healthcare Analytics Dashboard

An interactive Streamlit dashboard for analyzing hospital operations data — patient demographics, billing, admissions, medication trends, and test outcomes — with an AI-generated executive summary built in.

**[🔗 Live Demo](#)** *(add your Streamlit Cloud link here after deploying)*

![Dashboard Preview](screenshot.png)
*(add a screenshot of the dashboard here — drag an image file into this repo and update the filename above)*

---

## ✨ Features

- **Dynamic filtering** by Blood Type and Medical Condition, applied across every chart and KPI in real time
- **KPI summary cards** — total patients, total billing, average billing per patient, and top medical condition, each with context (e.g. % of total patient base)
- **Blood type & medical condition breakdowns** as bar charts
- **Admissions vs. discharges timeline** as a dual-axis line chart
- **Top 10 doctors by patient load**
- **Donut charts** for admission type, medication, test results, and insurance provider distribution — each with the total count shown in the center
- **🤖 AI Insights & Recommendations** — on demand, sends a live data summary to a Groq-hosted LLM (Llama 3.3 70B) and returns structured, executive-level insights, risks, and recommendations

## 🛠️ Tech Stack

- **Streamlit** — app framework and UI
- **Pandas** — data cleaning and aggregation
- **Plotly** — interactive charts (bar, line, donut)
- **KaggleHub** — dataset sourcing ([Healthcare Dataset](https://www.kaggle.com/datasets/prasad22/healthcare-dataset))
- **Groq API** (Llama 3.3 70B) — AI-generated insights

## 📦 Setup & Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/harminpatel793/healthcare-dashboard.git
   cd healthcare-dashboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.streamlit/secrets.toml` in the project root with:
   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   KAGGLE_USERNAME = "your_kaggle_username"
   KAGGLE_KEY = "your_kaggle_api_key"
   ```
   *(Get a free Groq API key at [console.groq.com](https://console.groq.com), and a Kaggle API token from your [Kaggle account settings](https://www.kaggle.com/settings).)*

4. Run the app:
   ```bash
   streamlit run Health.py
   ```

## 📊 Dataset

Uses the [Healthcare Dataset](https://www.kaggle.com/datasets/prasad22/healthcare-dataset) from Kaggle — synthetic hospital records covering patient demographics, admissions, billing, medications, and test outcomes.

## 📌 Notes

- Data is cached on load (`@st.cache_data`) to avoid re-downloading/reprocessing on every filter interaction.
- API keys are never committed to the repo — `.streamlit/secrets.toml` is excluded via `.gitignore`.

---

Built by [Harmin Patel](https://github.com/harminpatel793) · [LinkedIn](https://linkedin.com/in/harmin-patel)
