# Employee Attrition Dashboard

A Streamlit dashboard analyzing employee attrition drivers across 74,498 employees. Built to help HR teams understand why employees leave and where to focus retention efforts.

## Live Demo

[View on Streamlit Community Cloud](https://kayfa-internship-tv8yi8gz2tgybmkntbyew3.streamlit.app/)

## Key Insights

| Driver | Attrition Rate |
|---|---|
| On-site work | 52.8% |
| Remote work | 24.7% |
| Poor work-life balance | 60.2% |
| Excellent work-life balance | 35.7% |
| Overtime | 51.5% |
| No overtime | 45.5% |
| Female employees | 53.0% |
| Male employees | 42.9% |

**Bottom line:** Salary is NOT the issue — only a $46 difference between those who stayed and left. The real drivers are distance, flexibility, and workload.

## Dashboard Sections

- **Overview** — total headcount and overall attrition rate
- **Top Drivers** — remote work and overtime impact
- **Gender & Work-Life Balance** — breakdown by gender and balance rating
- **Stayed vs Left** — comparison of age, tenure, and distance from home
- **Income Analysis** — monthly income by attrition group
- **Job Role Breakdown** — attrition rate per department
- **Recommendations** — prioritized action items based on the data

## Run Locally

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
pip install -r requirements.txt
streamlit run streamlit.py
```

## Requirements

```
streamlit
plotly
pandas
```

## Tech Stack

- Python
- Streamlit
- Plotly