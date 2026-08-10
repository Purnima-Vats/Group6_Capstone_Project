# Student Course Completion — Data Analysis Capstone Project

Data preprocessing, EDA, visualization, and dashboarding on the
[Student Course Completion Prediction Dataset](https://www.kaggle.com/datasets/nisargpatel344/student-course-completion-prediction-dataset)
(100,000 students, 40 fields).

## Project structure

```
student-completion-capstone/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   └── processed/
│       └── clean_student_data.csv
├── notebooks/
│   ├── 01_data_quality_assessment.ipynb
│   ├── 02_data_cleaning_preprocessing.ipynb
│   └── 03_exploratory_data_analysis.ipynb
├── reports/
│   ├── quality_report.csv
│   └── Final_Project_Report.pdf
├── dashboard/
│   ├── dashboard_app.py
│   └── requirements.txt
└── presentation/
    └── Capstone_Project_Presentation.pdf
```

`presentation/` holds the slide deck for the project walkthrough, handled separately by the team.

## How the pieces fit together

1. **`Final_Project_Report.pdf`** — start here. Business problem, data dictionary summary, data
   quality summary, business insights, and recommendations, all pulled from actually running the
   notebooks below against the full dataset.
2. **`notebooks/01_data_quality_assessment.ipynb`** — loads the data and profiles it (missing
   values, duplicates, invalid records, outliers). Produces `reports/quality_report.csv`.
3. **`notebooks/02_data_cleaning_preprocessing.ipynb`** — resolves every issue from the quality
   report, engineers features (`engagement_score`, `engagement_tier`, `performance_score`, etc).
   Produces `data/processed/clean_student_data.csv`.
4. **`notebooks/03_exploratory_data_analysis.ipynb`** — 16 visualizations across univariate,
   bivariate, and multivariate analysis, each with a written insight tied to a business question.
5. **`dashboard/dashboard_app.py`** — interactive Streamlit dashboard built on the cleaned dataset.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Getting the data

The notebooks look for the data in this order:

1. `data/raw/Course_Completion_Prediction.csv` (place the full CSV here manually), or
2. a live Kaggle download via `kagglehub` (requires Kaggle API credentials set up locally), or
3. `data/raw/sample_200.csv` (a small sample, included for a quick dry run of the code)

To download via Kaggle directly:

```bash
pip install kagglehub
python -c "import kagglehub; print(kagglehub.dataset_download('nisargpatel344/student-course-completion-prediction-dataset'))"
```

Then copy the CSV from the printed path into `data/raw/Course_Completion_Prediction.csv`.

### Running the notebooks

```bash
jupyter notebook notebooks/
```

Run them in order: 01 → 02 → 03. Each one depends on the output of the previous one.

### Running the dashboard

```bash
cd dashboard
pip install -r requirements.txt
streamlit run dashboard_app.py
```

Opens at `http://localhost:8501`. Make sure `data/processed/clean_student_data.csv` exists first
(run notebooks 01 and 02, or use the one already included in this repo).

## Key findings (full detail in the report)

- Overall completion rate: **49.0%**, close to perfectly balanced.
- **Engagement tier is the strongest driver found**: High engagement students complete at 58.2%
  versus 39.7% for Low engagement, an 18.5 point gap.
- **Free enrollments complete ~10 points lower** than paid enrollments.
- **`Progress_Percentage` is not a reliable completion signal** — 29.3% of completed students
  logged under 50% progress. `Video_Completion_Rate` and engagement metrics are more reliable.
- **Course category and difficulty level have almost no effect** on completion rate.

## Notes

- `Name` is excluded from all analysis and the dashboard (PII).
- The dataset itself was found to have zero missing values and zero duplicates at full scale —
  see `reports/quality_report.csv` for the full profiling output.