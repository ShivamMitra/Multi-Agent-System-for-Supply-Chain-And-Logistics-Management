import streamlit as st
import time
from agent import (
    ElectronicComponentAgent,
    ProductionSchedulerAgent,
    LogisticsManagerAgent,
    DemandForecastAgent
)

st.set_page_config(page_title="Multi-Agent Supply Chain Dashboard", layout="wide")
st.title("📦 Multi-Agent Supply Chain System Dashboard")

# Shared context for memory
if 'context' not in st.session_state:
    st.session_state['context'] = {}
context = st.session_state['context']

# Sidebar controls
st.sidebar.header("Controls")
run_agents = st.sidebar.button("Run Full Orchestration")

# Agent 4: Demand Forecasting
with st.expander("Agent 4: Market & Customer Demand Forecasting", expanded=True):
    if st.button("Run Demand Forecast", key="forecast") or run_agents:
        forecast_agent = DemandForecastAgent(context=context)
        historical_sales = [
            {"product": "LM741", "region": "Europe", "sales": [100, 120, 130, 110]},
            {"product": "LM358", "region": "North America", "sales": [90, 95, 100, 105]},
            {"product": "OP07", "region": "Asia", "sales": [60, 70, 80, 75]}
        ]
        market_trends = {"Europe": "Stable", "North America": "Growing", "Asia": "Volatile"}
        seasonality = {"Q1": "Low", "Q2": "Medium", "Q3": "High", "Q4": "Medium"}
        economic_data = {"Europe": "Inflation 2%", "North America": "GDP growth 3%", "Asia": "Currency fluctuation"}
        customer_profiles = [
            {"customer_id": 1, "region": "Europe", "preferences": ["LM741", "OP07"]},
            {"customer_id": 2, "region": "North America", "preferences": ["LM358"]}
        ]
        inventory = {"LM741": 300, "LM358": 150, "OP07": 80}
        competition = {"LM741": 2.50, "LM358": 2.40, "OP07": 2.60}
        feedback = [
            "LM741 is reliable but sometimes out of stock.",
            "LM358 price is competitive.",
            "OP07 needs better documentation."
        ]
        with st.spinner("Forecasting demand..."):
            forecast = forecast_agent.generate_demand_forecast(
                historical_sales, market_trends, seasonality, economic_data,
                customer_profiles, inventory, competition, feedback
            )
            context['demand_forecast'] = forecast
        st.success("Demand forecast complete!")
        st.code(forecast, language="markdown")
    elif 'demand_forecast' in context:
        st.code(context['demand_forecast'], language="markdown")

# Agent 2: Production Scheduling
with st.expander("Agent 2: Production & Inventory Optimization", expanded=True):
    if st.button("Run Production Scheduler", key="prod") or run_agents:
        scheduler = ProductionSchedulerAgent(context=context)
        components = [
            {"part_number": "LM741", "lead_time": 14, "available_qty": 1200},
            {"part_number": "LM358", "lead_time": 10, "available_qty": 900},
            {"part_number": "OP07", "lead_time": 21, "available_qty": 500}
        ]
        stock_levels = {"LM741": 300, "LM358": 150, "OP07": 80}
        production_capacity = 200
        with st.spinner("Scheduling production..."):
            plan = scheduler.generate_production_plan(components, stock_levels, production_capacity)
            context['production_plan'] = plan
        st.success("Production plan generated!")
        st.code(plan, language="markdown")
    elif 'production_plan' in context:
        st.code(context['production_plan'], language="markdown")

# Agent 1: Component Sourcing
with st.expander("Agent 1: Component Sourcing & Risk Management", expanded=True):
    if st.button("Run Sourcing Agent", key="source") or run_agents:
        sourcing_agent = ElectronicComponentAgent(context=context)
        part_numbers = ["LM741", "LM358", "OP07"]
        sourced = []
        with st.spinner("Sourcing components..."):
            for pn in part_numbers:
                comp = sourcing_agent.source_component(pn, quantity=200)
                if comp:
                    sourced.append(f"{pn}: sourced {comp.stock} units, risk score {comp.risk_score}")
            delivery_plan = "; ".join(sourced)
            context['delivery_plan'] = delivery_plan
        st.success("Sourcing complete!")
        st.code(delivery_plan, language="markdown")
    elif 'delivery_plan' in context:
        st.code(context['delivery_plan'], language="markdown")

# Agent 3: Logistics
with st.expander("Agent 3: Global Logistics & Fulfillment", expanded=True):
    if st.button("Run Logistics Agent", key="logistics") or run_agents:
        logistics_agent = LogisticsManagerAgent(context=context)
        finished_goods = [
            {"part_number": "LM741", "quantity": 400, "destination": "Berlin"},
            {"part_number": "LM358", "quantity": 300, "destination": "New York"},
            {"part_number": "OP07", "quantity": 200, "destination": "Tokyo"}
        ]
        locations = {
            "Berlin": "Berlin Warehouse, Germany",
            "New York": "NYC Fulfillment Center, USA",
            "Tokyo": "Tokyo Logistics Hub, Japan"
        }
        timelines = {
            "LM741": "2025-08-20",
            "LM358": "2025-08-18",
            "OP07": "2025-08-25"
        }
        with st.spinner("Planning logistics..."):
            plan = logistics_agent.generate_logistics_plan(finished_goods, locations, timelines)
            context['logistics_plan'] = plan
        st.success("Logistics plan generated!")
        st.code(plan, language="markdown")
    elif 'logistics_plan' in context:
        st.code(context['logistics_plan'], language="markdown")

# Context viewer
with st.expander("🔎 Shared Context (Memory)", expanded=False):
    st.json(context)
