<div align="center">

<h1>📊 MTTR Analysis Dashboard</h1>

<p>Interactive dashboard to track <strong>Mean Time To Repair</strong> across production lines, machines, and defect categories.</p>

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-red?style=flat-square)
![Plotly](https://img.shields.io/badge/Plotly-5.24.1-green?style=flat-square)

</div>

---


## 🚀 Live App

> **[👉 Click here to open the dashboard](https://dkxsds6bfnnebiz4jxkr4j.streamlit.app/)**

No installation needed — runs directly in your browser.

---

## 📋 How to Use

### Step 1 — Open the App
Click the live link above. The dashboard loads instantly.

### Step 2 — Download Sample Data *(Optional)*
Click the **"📥 Download Sample CSV (500 rows)"** button at the top of the app to get a ready-to-use file with the correct format.

### Step 3 — Prepare Your CSV

Your file must have exactly these **7 columns**:

| Column Name | Description | Example |
|---|---|---|
| `Line-ID` | Production line name | `Line-1` |
| `Machine-ID` | Machine name | `Machine-3` |
| `Start-Time` | Breakdown start time | `17-01-2025 06:00` |
| `End-Time` | Breakdown end time | `17-01-2025 08:05` |
| `Category Defect` | Main defect category | `Electrical Defect` |
| `Sub-Category Defect` | Specific defect type | `Relay Contactor` |
| `Down-Time` | Duration in minutes | `99.99` |

> ⚠️ **Date format must be `DD-MM-YYYY HH:MM`**

### Step 4 — Upload & Explore
Upload your CSV and the dashboard will automatically generate all charts.

---

## 📊 Features

| Feature | Description |
|---|---|
| 📈 Pareto Chart by Line | Rank lines by MTTR with cumulative % overlay |
| 🔧 Machine-wise MTTR | Select any line → see machine-level breakdown |
| 🔍 Loss-wise MTTR | Select any machine → drill into defect categories |
| 📋 Top 5 Defects by Line | Most frequent defects per line |
| 🏁 Cross-line Defects | Defects appearing across multiple machines/lines |
| 📥 Export Charts | Download any chart as an interactive HTML file |

---

## 🎛️ Filters

Use the **left sidebar** to:
- Filter by **date range**
- Set a **minimum Down-Time** threshold (e.g. show only breakdowns > 30 min)

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) — dashboard framework
- [Pandas](https://pandas.pydata.org/) — data processing
- [Plotly](https://plotly.com/) — interactive charts
- [NumPy](https://numpy.org/) — numerical operations

---

## 📁 Repository Structure

```
MTTR-Dashboard/
├── mttr_dashboard.py   # Main dashboard app
├── Sample_Data.csv     # Sample dataset (500 rows)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## 📬 Contact

Built by **Anand Soni** · [GitHub Profile](https://github.com/Anand-Sony)
