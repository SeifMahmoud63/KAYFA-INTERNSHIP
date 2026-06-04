import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Employee Attrition Insights", layout="wide")

st.title("Employee Attrition Dashboard")
st.caption("A full analysis of employee attrition drivers")

remote   = {"On-site": 52.8, "Remote": 24.7}
overtime = {"No Overtime": 45.5, "Overtime": 51.5}
gender   = {"Female": 53.0, "Male": 42.9}
wlb      = {"Poor": 60.2, "Fair": 57.6, "Good": 40.4, "Excellent": 35.7}
roles    = {"Education": 48.8, "Healthcare": 47.5, "Technology": 47.1,
            "Finance": 46.9, "Media": 46.8}
income   = {"Stayed": 7321, "Left": 7275}

st.subheader("Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Employees", "74,498")
c2.metric("Left", "35,370")
c3.metric("Stayed", "39,128")
c4.metric("Attrition Rate", "47.5%", delta="Very High", delta_color="inverse")

st.divider()

st.subheader("Top Attrition Drivers")
col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Remote vs On-site")
    fig = px.bar(
        x=list(remote.keys()),
        y=list(remote.values()),
        color=list(remote.keys()),
        color_discrete_map={"On-site": "#E24B4A", "Remote": "#639922"},
        text=[f"{v}%" for v in remote.values()],
    )
    fig.update_layout(showlegend=False, yaxis_title="Attrition %",
                      xaxis_title="", yaxis_range=[0, 70])
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
    st.info("Remote cuts attrition by 28 points — the biggest gap in the entire dataset")

with col2:
    st.markdown("##### Overtime")
    fig2 = px.bar(
        x=list(overtime.keys()),
        y=list(overtime.values()),
        color=list(overtime.keys()),
        color_discrete_map={"No Overtime": "#639922", "Overtime": "#E24B4A"},
        text=[f"{v}%" for v in overtime.values()],
    )
    fig2.update_layout(showlegend=False, yaxis_title="Attrition %",
                       xaxis_title="", yaxis_range=[0, 70])
    fig2.update_traces(textposition="outside")
    st.plotly_chart(fig2, use_container_width=True)
    st.warning("Overtime adds 6 points — it amplifies existing stress, not a standalone cause")

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.markdown("##### Attrition by Gender")
    fig3 = px.bar(
        x=list(gender.keys()),
        y=list(gender.values()),
        color=list(gender.keys()),
        color_discrete_map={"Female": "#D4537E", "Male": "#378ADD"},
        text=[f"{v}%" for v in gender.values()],
    )
    fig3.update_layout(showlegend=False, yaxis_title="Attrition %",
                       xaxis_title="", yaxis_range=[0, 70])
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)
    st.warning("10-point gap between female and male — needs a separate investigation")

with col4:
    st.markdown("##### Work-Life Balance")
    fig4 = px.bar(
        x=list(wlb.keys()),
        y=list(wlb.values()),
        color=list(wlb.keys()),
        color_discrete_sequence=["#E24B4A", "#EF9F27", "#97C459", "#1D9E75"],
        text=[f"{v}%" for v in wlb.values()],
    )
    fig4.update_layout(showlegend=False, yaxis_title="Attrition %",
                       xaxis_title="", yaxis_range=[0, 75])
    fig4.update_traces(textposition="outside")
    st.plotly_chart(fig4, use_container_width=True)
    st.error("Poor balance = 60.2% attrition — highest single value in the dataset")

st.divider()

col5, col6 = st.columns(2)

with col5:
    st.markdown("##### Stayed vs Left: Age, Tenure, Distance")
    fig5 = go.Figure()
    metrics = ["Avg Age", "Years at Company", "Distance (km)"]
    stayed  = [39.1, 16.4, 47.4]
    left    = [37.9, 14.9, 52.8]
    fig5.add_trace(go.Bar(name="Stayed", x=metrics, y=stayed,
                          marker_color="#378ADD", text=stayed, textposition="outside"))
    fig5.add_trace(go.Bar(name="Left", x=metrics, y=left,
                          marker_color="#E24B4A", text=left, textposition="outside"))
    fig5.update_layout(barmode="group", yaxis_title="Value", xaxis_title="")
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.markdown("##### Average Monthly Income")
    fig6 = px.bar(
        x=list(income.keys()),
        y=list(income.values()),
        color=list(income.keys()),
        color_discrete_map={"Stayed": "#378ADD", "Left": "#E24B4A"},
        text=[f"${v:,}" for v in income.values()],
    )
    fig6.update_layout(showlegend=False, yaxis_title="Income $",
                       xaxis_title="", yaxis_range=[7000, 7500])
    fig6.update_traces(textposition="outside")
    st.plotly_chart(fig6, use_container_width=True)
    st.success("Only $46 difference — salary is NOT driving attrition here")

st.divider()

st.subheader("Attrition by Job Role")
fig7 = px.bar(
    x=list(roles.values()),
    y=list(roles.keys()),
    orientation="h",
    color=list(roles.values()),
    color_continuous_scale=["#639922", "#EF9F27", "#E24B4A"],
    text=[f"{v}%" for v in roles.values()],
)
fig7.update_layout(showlegend=False, xaxis_title="Attrition %",
                   yaxis_title="", coloraxis_showscale=False)
fig7.update_traces(textposition="outside")
st.plotly_chart(fig7, use_container_width=True)
st.info("All roles are close — this is a company-wide problem, not sector-specific")

st.divider()

st.subheader("Key Recommendations")
r1, r2, r3 = st.columns(3)
r1.success("**Priority 1:** Expand remote and hybrid work — highest impact, lowest cost")
r2.warning("**Priority 2:** Fix overtime policy and improve work-life balance")
r3.error("**Priority 3:** Investigate the gender gap and review flexible work policies")

st.caption("Note: Salary increases are NOT recommended.")