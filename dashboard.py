import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_PATH = "cleaned_attrition_data.csv"
LOGO_PATH = "logo.png"

BLUE = "#4C78A8"
RED = "#E45756"
ORANGE = "#F58518"
GREEN = "#54A24B"
GRAY = "#7A7A7A"


st.set_page_config(
    page_title="Kayfa - Employee Attrition Command Center",
    page_icon="chart_with_upwards_trend",
    layout="wide",
)
st.logo(LOGO_PATH)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


df = load_data()
overall_rate = df["attrition"].mean() * 100


def pct(value):
    return f"{value:.1f}%"


def add_company_average(fig, x_values, orientation="horizontal"):
    if orientation == "horizontal":
        fig.add_trace(
            go.Scatter(
                x=list(x_values),
                y=[overall_rate] * len(list(x_values)),
                mode="lines",
                line=dict(color=GRAY, dash="dash", width=2),
                name=f"Company average ({overall_rate:.1f}%)",
            )
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=[overall_rate] * len(list(x_values)),
                y=list(x_values),
                mode="lines",
                line=dict(color=GRAY, dash="dash", width=2),
                name=f"Company average ({overall_rate:.1f}%)",
            )
        )


def style_bar_chart(fig, y_max=None, legend=True):
    fig.update_traces(textposition="outside", cliponaxis=False, selector=dict(type="bar"))
    fig.update_layout(
        height=430,
        margin=dict(t=70, r=30, b=55, l=55),
        legend_title_text="",
        showlegend=legend,
    )
    if y_max:
        fig.update_yaxes(range=[0, y_max])
    return fig


def insight(text, action):
    st.info(f"Insight: {text}\n\nCTA: {action}")


def metric_row():
    total = len(df)
    left = int(df["attrition"].sum())
    stayed = total - left
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Employees", f"{total:,}")
    c2.metric("Employees Left", f"{left:,}")
    c3.metric("Employees Stayed", f"{stayed:,}")
    c4.metric("Attrition Rate", pct(overall_rate), delta="Very high", delta_color="inverse")


def home_page():
    left, right = st.columns([0.72, 0.28], vertical_alignment="center")
    with left:
        st.title("Week #1 Task: Employee Attrition Command Center")
        st.caption("A retention dashboard for finding where attrition risk is highest and what HR should do next.")
    with right:
        st.image(LOGO_PATH, width=180)

    metric_row()
    st.divider()

    drivers = pd.DataFrame(
        [
            {
                "Driver": "Work-Life Balance",
                "Gap": df[df["work_life_balance"].isin(["Poor", "Fair"])]["attrition"].mean() * 100
                - df[df["work_life_balance"].isin(["Good", "Excellent"])]["attrition"].mean() * 100,
                "Employees Affected": int(df["work_life_balance"].isin(["Poor", "Fair"]).sum()),
            },
            {
                "Driver": "Remote Work",
                "Gap": df[df["remote_work"] == 0]["attrition"].mean() * 100
                - df[df["remote_work"] == 1]["attrition"].mean() * 100,
                "Employees Affected": int((df["remote_work"] == 0).sum()),
            },
            {
                "Driver": "Overtime",
                "Gap": df[df["overtime"] == 1]["attrition"].mean() * 100
                - df[df["overtime"] == 0]["attrition"].mean() * 100,
                "Employees Affected": int((df["overtime"] == 1).sum()),
            },
        ]
    )
    drivers["Potential Saves"] = (drivers["Gap"] / 100 * drivers["Employees Affected"] * 0.25).astype(int)
    drivers = drivers.sort_values("Gap", ascending=False)

    fig = px.bar(
        drivers,
        x="Driver",
        y="Gap",
        text="Gap",
        color="Driver",
        title="Top Retention Levers by Attrition Gap",
        labels={"Gap": "Attrition Gap (percentage points)", "Driver": "Retention Lever"},
        color_discrete_map={"Work-Life Balance": RED, "Remote Work": BLUE, "Overtime": ORANGE},
    )
    fig.update_traces(texttemplate="%{text:.1f}pp")
    style_bar_chart(fig, y_max=max(32, drivers["Gap"].max() + 5))
    st.plotly_chart(fig, use_container_width=True)
    top = drivers.iloc[0]
    insight(
        f"{top['Driver']} has the widest gap at {top['Gap']:.1f} percentage points.",
        f"Start the first pilot there; closing only 25% of the gap could retain about {top['Potential Saves']:,} employees.",
    )


def foundations_page():
    st.title("Foundations: Q1-Q3")
    q1, q2, q3 = st.tabs(["Q1 Job Role", "Q2 Overtime", "Q3 Remote Work"])

    with q1:
        role_attrition = df.groupby("job_role")["attrition"].agg(["mean", "count"]).reset_index()
        role_attrition["Attrition Rate"] = role_attrition["mean"] * 100
        role_attrition = role_attrition.sort_values("Attrition Rate", ascending=True)
        fig = px.bar(
            role_attrition,
            x="Attrition Rate",
            y="job_role",
            orientation="h",
            text="Attrition Rate",
            title="Attrition Rate by Job Role Shows a Company-Wide Problem",
            labels={"Attrition Rate": "Attrition Rate (%)", "job_role": "Job Role"},
            color_discrete_sequence=[BLUE],
        )
        fig.update_traces(texttemplate="%{text:.1f}%")
        add_company_average(fig, role_attrition["job_role"], orientation="vertical")
        style_bar_chart(fig, legend=True)
        st.plotly_chart(fig, use_container_width=True)
        top_role = role_attrition.sort_values("Attrition Rate", ascending=False).iloc[0]
        insight(
            f"{top_role['job_role']} has the highest rate at {top_role['Attrition Rate']:.1f}%, but all roles sit close to the company average.",
            "Run a company-wide retention program, using the highest-rate roles as the first pilot groups.",
        )

    with q2:
        overtime = df.groupby("overtime")["attrition"].mean().reset_index()
        overtime["Overtime Status"] = overtime["overtime"].map({0: "No Overtime", 1: "Overtime"})
        overtime["Attrition Rate"] = overtime["attrition"] * 100
        fig = px.bar(
            overtime,
            x="Overtime Status",
            y="Attrition Rate",
            color="Overtime Status",
            text="Attrition Rate",
            title="Overtime Employees Are More Likely to Leave",
            labels={"Overtime Status": "Overtime Status", "Attrition Rate": "Attrition Rate (%)"},
            color_discrete_map={"No Overtime": BLUE, "Overtime": RED},
        )
        fig.update_traces(texttemplate="%{text:.1f}%")
        add_company_average(fig, overtime["Overtime Status"])
        style_bar_chart(fig, y_max=65)
        st.plotly_chart(fig, use_container_width=True)
        gap = overtime.loc[overtime["Overtime Status"] == "Overtime", "Attrition Rate"].iloc[0] - overtime.loc[overtime["Overtime Status"] == "No Overtime", "Attrition Rate"].iloc[0]
        insight(
            f"Overtime raises attrition by {gap:.1f} percentage points.",
            "Audit teams with chronic overtime and replace repeated mandatory overtime with comp time, staffing support, or flex days.",
        )

    with q3:
        remote = df.groupby("remote_work")["attrition"].mean().reset_index()
        remote["Work Type"] = remote["remote_work"].map({0: "On-site", 1: "Remote"})
        remote["Attrition Rate"] = remote["attrition"] * 100
        fig = px.bar(
            remote,
            x="Work Type",
            y="Attrition Rate",
            color="Work Type",
            text="Attrition Rate",
            title="Remote Employees Leave Far Less Often Than On-site Employees",
            labels={"Work Type": "Work Type", "Attrition Rate": "Attrition Rate (%)"},
            color_discrete_map={"On-site": RED, "Remote": BLUE},
        )
        fig.update_traces(texttemplate="%{text:.1f}%")
        add_company_average(fig, remote["Work Type"])
        style_bar_chart(fig, y_max=65)
        st.plotly_chart(fig, use_container_width=True)
        gap = remote.loc[remote["Work Type"] == "On-site", "Attrition Rate"].iloc[0] - remote.loc[remote["Work Type"] == "Remote", "Attrition Rate"].iloc[0]
        insight(
            f"Remote work has the largest simple gap: {gap:.1f} percentage points lower attrition than on-site work.",
            "Pilot hybrid work in high-attrition teams and measure whether the gap holds over the next 6 months.",
        )


def segmentation_page():
    st.title("Segmentation: Q4-Q7")
    q4, q5, q6, q7 = st.tabs(["Q4 Pay and Level", "Q5 Tenure", "Q6 Satisfaction", "Q7 Life Stage"])

    with q4:
        rows = []
        for level in ["Entry", "Mid", "Senior"]:
            sub = df[df["job_level"] == level].copy()
            sub["Income Quartile"] = pd.qcut(sub["monthly_income"], 4, labels=["Q1 Lowest", "Q2", "Q3", "Q4 Highest"])
            for quartile, rate in (sub.groupby("Income Quartile", observed=False)["attrition"].mean() * 100).items():
                rows.append({"Job Level": level, "Income Quartile": quartile, "Attrition Rate": rate})
        pay_df = pd.DataFrame(rows)
        fig = px.bar(
            pay_df,
            x="Income Quartile",
            y="Attrition Rate",
            color="Job Level",
            barmode="group",
            text="Attrition Rate",
            title="Attrition by Pay Quartile Within Each Job Level",
            labels={"Attrition Rate": "Attrition Rate (%)"},
            color_discrete_map={"Entry": RED, "Mid": ORANGE, "Senior": BLUE},
            category_orders={"Income Quartile": ["Q1 Lowest", "Q2", "Q3", "Q4 Highest"], "Job Level": ["Entry", "Mid", "Senior"]},
        )
        fig.update_traces(texttemplate="%{text:.1f}%")
        style_bar_chart(fig, y_max=75)
        st.plotly_chart(fig, use_container_width=True)
        insight(
            "Job level dominates pay quartile; Entry-level attrition is far above Senior attrition even inside pay bands.",
            "Prioritize faster Entry-to-Mid progression before broad salary increases.",
        )

    with q5:
        tenure_order = ["0-2 Years", "3-5 Years", "6-10 Years", "11-20 Years", "21+ Years"]
        tenure = df.assign(
            Tenure=pd.cut(
                df["years_at_company"],
                bins=[0, 2, 5, 10, 20, 51],
                labels=tenure_order,
                include_lowest=True,
            )
        )
        tenure = tenure.groupby("Tenure", observed=False)["attrition"].mean().reset_index()
        tenure["Attrition Rate"] = tenure["attrition"] * 100
        fig = px.bar(
            tenure,
            x="Tenure",
            y="Attrition Rate",
            text="Attrition Rate",
            title="Attrition Is Highest During the First Five Years",
            labels={"Tenure": "Years at Company", "Attrition Rate": "Attrition Rate (%)"},
            color_discrete_sequence=[BLUE],
            category_orders={"Tenure": tenure_order},
        )
        fig.update_traces(texttemplate="%{text:.1f}%")
        add_company_average(fig, tenure["Tenure"])
        style_bar_chart(fig, y_max=62)
        st.plotly_chart(fig, use_container_width=True)
        peak_row = tenure.sort_values("Attrition Rate", ascending=False).iloc[0]
        late_rate = tenure.loc[tenure["Tenure"] == "21+ Years", "Attrition Rate"].iloc[0]
        insight(
            f"{peak_row['Tenure']} is the peak at {peak_row['Attrition Rate']:.1f}% attrition; after 10 years, attrition drops to about {late_rate:.1f}%.",
            "Strengthen onboarding, mentoring, and 30/60/90-day check-ins before year five.",
        )

    with q6:
        sat_order = ["Low", "Medium", "High", "Very High"]
        wlb_order = ["Poor", "Fair", "Good", "Excellent"]
        combo = df.groupby(["job_satisfaction", "work_life_balance"], observed=False)["attrition"].mean().reset_index()
        combo["Attrition Rate"] = combo["attrition"] * 100
        pivot = combo.pivot(index="job_satisfaction", columns="work_life_balance", values="Attrition Rate").reindex(index=sat_order, columns=wlb_order)
        fig = px.imshow(
            pivot,
            text_auto=".1f",
            color_continuous_scale="RdYlGn_r",
            title="Attrition Heatmap by Job Satisfaction and Work-Life Balance",
            labels={"x": "Work-Life Balance", "y": "Job Satisfaction", "color": "Attrition Rate (%)"},
            aspect="auto",
        )
        fig.update_layout(height=470, margin=dict(t=70, r=30, b=55, l=80))
        st.plotly_chart(fig, use_container_width=True)
        worst = combo.sort_values("Attrition Rate", ascending=False).iloc[0]
        insight(
            f"{worst['job_satisfaction']} satisfaction plus {worst['work_life_balance']} work-life balance reaches {worst['Attrition Rate']:.1f}% attrition.",
            "Flag employees who report both low satisfaction and poor or fair balance, then schedule a manager follow-up within two weeks.",
        )

    with q7:
        age_order = ["18-25", "26-35", "36-45", "46-60"]
        life = df.assign(Age_Group=pd.cut(df["age"], bins=[17, 25, 35, 45, 60], labels=age_order))
        life = life.groupby(["Age_Group", "marital_status"], observed=False)["attrition"].mean().reset_index()
        life["Attrition Rate"] = life["attrition"] * 100
        fig = px.bar(
            life,
            x="Age_Group",
            y="Attrition Rate",
            color="marital_status",
            barmode="group",
            text="Attrition Rate",
            title="Young Single Employees Are the Highest-Risk Life Stage",
            labels={"Age_Group": "Age Group", "marital_status": "Marital Status", "Attrition Rate": "Attrition Rate (%)"},
            color_discrete_map={"Single": RED, "Divorced": ORANGE, "Married": BLUE},
            category_orders={"Age_Group": age_order, "marital_status": ["Single", "Divorced", "Married"]},
        )
        fig.update_traces(texttemplate="%{text:.1f}%")
        add_company_average(fig, age_order)
        style_bar_chart(fig, y_max=82)
        st.plotly_chart(fig, use_container_width=True)

        dep = df.groupby("number_of_dependents")["attrition"].mean().reset_index()
        dep["Attrition Rate"] = dep["attrition"] * 100
        fig2 = px.bar(
            dep,
            x="number_of_dependents",
            y="Attrition Rate",
            text="Attrition Rate",
            title="Employees With More Dependents Leave Less Often",
            labels={"number_of_dependents": "Number of Dependents", "Attrition Rate": "Attrition Rate (%)"},
            color_discrete_sequence=[BLUE],
        )
        fig2.update_traces(texttemplate="%{text:.1f}%")
        add_company_average(fig2, dep["number_of_dependents"])
        style_bar_chart(fig2, y_max=60)
        st.plotly_chart(fig2, use_container_width=True)
        highest = life.sort_values("Attrition Rate", ascending=False).iloc[0]
        insight(
            f"The highest-risk group is {highest['Age_Group']}, {highest['marital_status']} at {highest['Attrition Rate']:.1f}% attrition.",
            "Retain young single employees with growth paths, mentoring, and belonging programs rather than family-oriented benefits.",
        )


def synthesis_page():
    st.title("Synthesis: Q8-Q10")
    q8, q9, q10 = st.tabs(["Q8 Growth", "Q9 Risk Profile", "Q10 Top Priority"])

    with q8:
        promo = df.groupby("number_of_promotions")["attrition"].mean().reset_index()
        promo["Attrition Rate"] = promo["attrition"] * 100
        fig = px.bar(
            promo,
            x="number_of_promotions",
            y="Attrition Rate",
            text="Attrition Rate",
            title="Promotions Dramatically Reduce Attrition",
            labels={"number_of_promotions": "Number of Promotions", "Attrition Rate": "Attrition Rate (%)"},
            color_discrete_sequence=[BLUE],
        )
        fig.update_traces(texttemplate="%{text:.1f}%")
        add_company_average(fig, promo["number_of_promotions"])
        style_bar_chart(fig, y_max=58)
        st.plotly_chart(fig, use_container_width=True)

        level_order = ["Entry", "Mid", "Senior"]
        level = df.groupby("job_level")["attrition"].mean().reindex(level_order).reset_index()
        level["Attrition Rate"] = level["attrition"] * 100
        fig2 = px.bar(
            level,
            x="job_level",
            y="Attrition Rate",
            text="Attrition Rate",
            title="Entry-Level Employees Leave at About Three Times the Senior Rate",
            labels={"job_level": "Job Level", "Attrition Rate": "Attrition Rate (%)"},
            color_discrete_sequence=[BLUE],
            category_orders={"job_level": level_order},
        )
        fig2.update_traces(texttemplate="%{text:.1f}%")
        style_bar_chart(fig2, y_max=72, legend=False)
        st.plotly_chart(fig2, use_container_width=True)

        lead_yes = df[df["leadership_opportunities"] == 1]["attrition"].mean() * 100
        lead_no = df[df["leadership_opportunities"] == 0]["attrition"].mean() * 100
        innov_yes = df[df["innovation_opportunities"] == 1]["attrition"].mean() * 100
        innov_no = df[df["innovation_opportunities"] == 0]["attrition"].mean() * 100
        opps = pd.DataFrame(
            {
                "Opportunity": ["Leadership", "Leadership", "Innovation", "Innovation"],
                "Status": ["No", "Yes", "No", "Yes"],
                "Attrition Rate": [lead_no, lead_yes, innov_no, innov_yes],
            }
        )
        fig3 = px.bar(
            opps,
            x="Opportunity",
            y="Attrition Rate",
            color="Status",
            barmode="group",
            text="Attrition Rate",
            title="Leadership and Innovation Opportunities Reduce Attrition",
            labels={"Opportunity": "Opportunity", "Attrition Rate": "Attrition Rate (%)"},
            color_discrete_map={"No": RED, "Yes": BLUE},
        )
        fig3.update_traces(texttemplate="%{text:.1f}%")
        style_bar_chart(fig3, y_max=55)
        st.plotly_chart(fig3, use_container_width=True)

        zero_promo_pct = (df["number_of_promotions"] == 0).mean() * 100
        lead_pct = df["leadership_opportunities"].mean() * 100
        innov_pct = df["innovation_opportunities"].mean() * 100
        insight(
            f"Career stagnation is the clearest predictor: {zero_promo_pct:.0f}% have zero promotions, only {lead_pct:.0f}% get leadership opportunities, and only {innov_pct:.0f}% get innovation roles.",
            "Create annual growth opportunities and fast-track strong Entry-level employees into Mid-level roles.",
        )

    with q9:
        risk4 = df[(df["overtime"] == 1) & (df["remote_work"] == 0) & (df["work_life_balance"] == "Poor") & (df["job_satisfaction"] == "Low")]
        risk3 = df[(df["overtime"] == 1) & (df["remote_work"] == 0) & (df["work_life_balance"] == "Poor")]
        profile = pd.DataFrame(
            {
                "Profile": ["Company Average", "3-Factor Risk Profile", "4-Factor Risk Profile"],
                "Attrition Rate": [overall_rate, risk3["attrition"].mean() * 100, risk4["attrition"].mean() * 100],
                "Employees": [len(df), len(risk3), len(risk4)],
            }
        )
        fig = px.bar(
            profile,
            x="Profile",
            y="Attrition Rate",
            color="Profile",
            text="Attrition Rate",
            title="Stacked Risk Factors Create the Highest Attrition Profile",
            labels={"Profile": "Employee Profile", "Attrition Rate": "Attrition Rate (%)"},
            color_discrete_map={"Company Average": BLUE, "3-Factor Risk Profile": ORANGE, "4-Factor Risk Profile": RED},
        )
        fig.update_traces(texttemplate="%{text:.1f}%")
        style_bar_chart(fig, y_max=90)
        st.plotly_chart(fig, use_container_width=True)
        insight(
            f"The 4-factor profile is severe but small at {len(risk4):,} employees; the 3-factor version catches {len(risk3):,} employees.",
            "Query current employees with three or more risk factors and offer schedule flexibility or remote days first.",
        )

    with q10:
        drivers = {
            "Remote Work": {
                "Gap": df[df["remote_work"] == 0]["attrition"].mean() * 100 - df[df["remote_work"] == 1]["attrition"].mean() * 100,
                "Above Baseline": df[df["remote_work"] == 0]["attrition"].mean() * 100 - overall_rate,
                "Employees Affected": int((df["remote_work"] == 0).sum()),
            },
            "Work-Life Balance": {
                "Gap": df[df["work_life_balance"].isin(["Poor", "Fair"])]["attrition"].mean() * 100
                - df[df["work_life_balance"].isin(["Good", "Excellent"])]["attrition"].mean() * 100,
                "Above Baseline": df[df["work_life_balance"].isin(["Poor", "Fair"])]["attrition"].mean() * 100 - overall_rate,
                "Employees Affected": int(df["work_life_balance"].isin(["Poor", "Fair"]).sum()),
            },
            "Overtime Reduction": {
                "Gap": df[df["overtime"] == 1]["attrition"].mean() * 100 - df[df["overtime"] == 0]["attrition"].mean() * 100,
                "Above Baseline": df[df["overtime"] == 1]["attrition"].mean() * 100 - overall_rate,
                "Employees Affected": int((df["overtime"] == 1).sum()),
            },
        }
        priority = pd.DataFrame([{"Priority": k, **v} for k, v in drivers.items()])
        priority["Estimated Saves"] = (priority["Gap"] / 100 * priority["Employees Affected"] * 0.25).astype(int)
        priority = priority.sort_values("Estimated Saves", ascending=False)
        fig = px.bar(
            priority,
            x="Priority",
            y="Gap",
            color="Priority",
            text="Gap",
            title="Top Attrition Drivers Ranked by Potential Impact",
            labels={"Priority": "Intervention", "Gap": "Attrition Gap Between Groups (pp)"},
            hover_data={"Above Baseline": ":.1f", "Employees Affected": ":,", "Estimated Saves": ":,"},
            color_discrete_map={"Remote Work": BLUE, "Work-Life Balance": RED, "Overtime Reduction": ORANGE},
        )
        fig.update_traces(texttemplate="%{text:.1f}pp")
        style_bar_chart(fig, y_max=32)
        st.plotly_chart(fig, use_container_width=True)
        top = priority.iloc[0]
        insight(
            f"{top['Priority']} ranks first by potential impact: {top['Gap']:.1f}pp gap, {top['Employees Affected']:,} employees affected, and about {top['Estimated Saves']:,} retained if HR closes 25% of the gap.",
            "Pilot hybrid or flexible scheduling for high-attrition on-site teams, then measure attrition again after 6 months.",
        )


pages = [
    st.Page(home_page, title="Home", icon=":material/home:"),
    st.Page(foundations_page, title="Foundations: Q1-Q3", icon=":material/filter_1:"),
    st.Page(segmentation_page, title="Segmentation: Q4-Q7", icon=":material/grouped_bar_chart:"),
    st.Page(synthesis_page, title="Synthesis: Q8-Q10", icon=":material/analytics:"),
]

st.navigation(pages).run()
