"""Sales Pipeline Analytics - Streamlit App. Run with: streamlit run app.py"""

import asyncio
import time
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from agents import Runner, set_default_openai_key
from openai.types.responses import ResponseTextDeltaEvent

from config import get_config
from agent_defs import sales_funnel_agent
from services.models import Deal, SalesFunnel, FunnelStage

st.set_page_config(page_title="Sales Pipeline Analytics", page_icon="📊", layout="wide")

try:
    cfg = get_config()
    set_default_openai_key(cfg["openai_api_key"])
except ValueError as e:
    st.error(str(e))
    st.stop()

def build_sample_teams():
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    t15 = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")
    t30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    deals = [
        Deal("d1", "Software Deal", "FistaSolutions", 600000.0, FunnelStage.OPPORTUNITY, t15, t, 0.9, "Mohammad Usman"),
        Deal("d2", "Agentic AI", "AI Soft", 120000.0, FunnelStage.NEGOTIATION, t30, t, 1.0, "Asif Iqbal"),
    ]
    return SalesFunnel("ent_123", deals, True), SalesFunnel("basic_123", deals[:1], False)

enterprise_team, basic_team = build_sample_teams()

st.sidebar.header("Plan and pipeline")
plan = st.sidebar.radio("Plan", ["Enterprise", "Basic"])
selected_team = enterprise_team if plan == "Enterprise" else basic_team

metrics = asyncio.run(selected_team.get_metrices())
st.sidebar.metric("Total deals", metrics["total"])
st.sidebar.metric("Total value", f"${metrics['value']:,.0f}")

st.title("Sales Pipeline Analytics")

# Funnel by stage (ordered list of stages, count from metrics)
stage_order = [s.value for s in FunnelStage]
stage_counts = [metrics["stages"].get(s, 0) for s in stage_order]
funnel_df = pd.DataFrame({"Stage": stage_order, "Count": stage_counts})
if funnel_df["Count"].sum() > 0:
    st.subheader("Funnel by stage")
    fig = px.funnel(funnel_df, x="Count", y="Stage", title="Deals by funnel stage")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("No deals in pipeline — funnel chart will appear when you have deals.")

st.markdown("---")
prompt = st.text_area("Customize your query", value="Please analyze my sales funnel and provide recommendations.", height=80)

if st.button("Run analysis", type="primary"):
    response_placeholder = st.empty()
    accumulated = ""
    try:
        result = Runner.run_streamed(sales_funnel_agent, prompt, context=selected_team)
        chunks = []
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                chunks.append(event.data.delta or "")
            await asyncio.sleep(0.01)
        for ch in chunks:
            accumulated += ch
            response_placeholder.markdown(accumulated)
            time.sleep(0.01)
    except Exception:
        st.error("Analysis failed.")
