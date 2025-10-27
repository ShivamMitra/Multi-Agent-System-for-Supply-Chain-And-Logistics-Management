import streamlit as st
import time
import pandas as pd
import plotly.express as px
import re
import json
from agent import (
    ElectronicComponentAgent,
    ProductionSchedulerAgent,
    LogisticsManagerAgent,
    DemandForecastAgent,
    ComponentSourcingAgent
)

# Page configuration
st.set_page_config(
    page_title="🤖 Multi-Agent Supply Chain Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; color: #1f77b4; text-align: center; margin-bottom: 1rem;}
    .agent-section {margin-bottom: 2rem; border: 1px solid #e6e6e6; border-radius: 10px; padding: 1.5rem;}
    .agent-header {color: #2e86c1; margin-bottom: 1rem;}
    .status-card {background-color: #f8f9fa; border-radius: 10px; padding: 1rem; margin: 0.5rem 0;}
    .success {border-left: 5px solid #2ecc71;}
    .warning {border-left: 5px solid #f39c12;}
    .error {border-left: 5px solid #e74c3c;}
    .agent-output {background-color: #f8f9fa; border-radius: 8px; padding: 1rem; margin: 1rem 0; border-left: 4px solid #3498db;}
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("<h1 class='main-header'>🤖 Multi-Agent Supply Chain System</h1>", unsafe_allow_html=True)
st.markdown("""
This dashboard provides real-time monitoring and control of the AI-powered supply chain management system.
The system consists of four specialized agents working together to optimize the supply chain process.
""")

 

# Initialize session state
if 'context' not in st.session_state:
    st.session_state['context'] = {}
    st.session_state['agent_status'] = {
        'demand_forecast': 'Not Run',
        'production_schedule': 'Not Run',
        'component_sourcing': 'Not Run',
        'logistics': 'Not Run'
    }
    st.session_state['last_run'] = None
    st.session_state['agent_outputs'] = {}
    st.session_state['result_timestamps'] = {}

context = st.session_state['context']

# Helper function to parse agent outputs
def parse_agent_output(output_text, agent_type):
    """Parse agent output text to extract structured data for visualization"""
    if not output_text:
        return None
    
    parsed_data = {
        'raw_output': output_text,
        'extracted_data': {}
    }
    
    try:
        if agent_type == 'demand_forecast':
            # Extract product mentions and quantities
            products = ['LM741', 'LM358', 'OP07']
            for product in products:
                if product in output_text:
                    # Look for numbers near product names
                    numbers = re.findall(rf'{product}.*?(\d+)', output_text, re.IGNORECASE)
                    if numbers:
                        parsed_data['extracted_data'][product] = {
                            'mentioned': True,
                            'quantities': [int(n) for n in numbers]
                        }
                    else:
                        parsed_data['extracted_data'][product] = {
                            'mentioned': True,
                            'quantities': []
                        }
        
        elif agent_type == 'production_schedule':
            # Extract production quantities and recommendations
            products = ['LM741', 'LM358', 'OP07']
            for product in products:
                if product in output_text:
                    numbers = re.findall(rf'{product}.*?(\d+)', output_text, re.IGNORECASE)
                    if numbers:
                        parsed_data['extracted_data'][product] = {
                            'production_quantities': [int(n) for n in numbers],
                            'recommendations': []
                        }
        
        elif agent_type == 'component_sourcing':
            # Handle Component objects directly
            if hasattr(output_text, 'part_number'):
                parsed_data['extracted_data'] = {
                    'part_number': output_text.part_number,
                    'manufacturer': output_text.manufacturer,
                    'price': output_text.price,
                    'stock': output_text.stock,
                    'lead_time': output_text.lead_time,
                    'risk_score': output_text.risk_score
                }
            # Handle string output
            elif isinstance(output_text, str):
                # Extract component information from text
                part_match = re.search(r'part_number["\']?\s*:\s*["\']?([^"\',\s]+)', output_text)
                manufacturer_match = re.search(r'manufacturer["\']?\s*:\s*["\']?([^"\',\s]+)', output_text)
                price_match = re.search(r'price["\']?\s*:\s*(\d+\.?\d*)', output_text)
                stock_match = re.search(r'stock["\']?\s*:\s*(\d+)', output_text)
                lead_time_match = re.search(r'lead_time["\']?\s*:\s*(\d+)', output_text)
                risk_match = re.search(r'risk_score["\']?\s*:\s*(\d+\.?\d*)', output_text)
                
                parsed_data['extracted_data'] = {
                    'part_number': part_match.group(1) if part_match else 'Unknown',
                    'manufacturer': manufacturer_match.group(1) if manufacturer_match else 'Unknown',
                    'price': float(price_match.group(1)) if price_match else 0.0,
                    'stock': int(stock_match.group(1)) if stock_match else 0,
                    'lead_time': int(lead_time_match.group(1)) if lead_time_match else 0,
                    'risk_score': float(risk_match.group(1)) if risk_match else 0.0
                }
        
        elif agent_type == 'logistics':
            # Extract logistics information
            destinations = ['Berlin', 'New York', 'Tokyo']
            for dest in destinations:
                if dest in output_text:
                    parsed_data['extracted_data'][dest] = {
                        'mentioned': True,
                        'transport_mode': 'Unknown'
                    }
                    
            # Try to identify transport modes
            transport_modes = []
            if 'air' in output_text.lower():
                transport_modes.append('Air')
            if 'sea' in output_text.lower():
                transport_modes.append('Sea')
            if 'road' in output_text.lower():
                transport_modes.append('Road')
            
            if transport_modes:
                parsed_data['extracted_data']['transport_modes'] = transport_modes
                
    except Exception as e:
        st.warning(f"Error parsing {agent_type} output: {e}")
    
    return parsed_data

# Helper to sanitize markdown-like output for clean text display
def _sanitize_output_text(text: str) -> str:
    try:
        # Remove bold/italic markers and bullet asterisks at line starts
        lines = str(text).splitlines()
        cleaned = []
        for ln in lines:
            cl = ln.replace('**', '').replace('__', '')
            cl = re.sub(r'^\s*[\-*]\s*', '', cl)
            cleaned.append(cl)
        return "\n".join(cleaned)
    except Exception:
        return text

def _extract_markdown_tables(text: str):
    try:
        lines = str(text).splitlines()
        tables = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if '|' in line and i + 1 < len(lines) and re.fullmatch(r"\s*\|?\s*[:\-\s\|]+\s*\|?\s*", lines[i+1]):
                header = line
                sep = lines[i+1]
                block = [header, sep]
                j = i + 2
                while j < len(lines) and '|' in lines[j] and lines[j].strip() != '':
                    block.append(lines[j])
                    j += 1
                def parse_row(r):
                    cells = [c.strip() for c in r.strip().split('|')]
                    if cells and cells[0] == '':
                        cells = cells[1:]
                    if cells and cells[-1] == '':
                        cells = cells[:-1]
                    return cells
                headers = parse_row(block[0])
                data_rows = [parse_row(r) for r in block[2:]]
                if headers and data_rows:
                    maxlen = max(len(headers), max((len(r) for r in data_rows), default=0))
                    headers = headers + [''] * (maxlen - len(headers))
                    norm_rows = [r + [''] * (maxlen - len(r)) for r in data_rows]
                    df = pd.DataFrame(norm_rows, columns=headers)
                    tables.append(df)
                i = j
                continue
            i += 1
        return tables
    except Exception:
        return []

# Function to update status
def update_agent_status(agent, status):
    st.session_state['agent_status'][agent] = status
    st.session_state['last_run'] = time.strftime("%Y-%m-%d %H:%M:%S")
    if status == 'Completed':
        st.session_state['result_timestamps'][agent] = time.time()
    # Do not rerun when marking as Running, to allow the work to complete.
    if status != 'Running':
        st.rerun()

# Function to clear old results when new ones are generated
def clear_old_results():
    """Clear old results to ensure fresh data is displayed"""
    if 'agent_outputs' in st.session_state:
        st.session_state['agent_outputs'] = {}

# Sidebar controls
with st.sidebar:
    st.title("🛠️ Controls")
    st.markdown("### Pipeline")
    run_pipeline = st.button("🚀 Run Complete Pipeline", use_container_width=True, type="primary", help="Execute Agents 1→4 in sequence")
    st.markdown("### Agents")
    run_forecast = st.button("1) 📈 Forecast Demand", use_container_width=True, help="Agent 1: Demand & Marketing Insights")
    run_production = st.button("2) 🏭 Schedule Production", use_container_width=True, help="Agent 2: Production & Inventory Optimization")
    run_sourcing = st.button("3) 🔍 Source Components", use_container_width=True, help="Agent 3: Component Sourcing & Risk")
    run_logistics = st.button("4) 🚚 Plan Logistics", use_container_width=True, help="Agent 4: Global Logistics & Fulfillment")
    st.markdown("### Data Management")
    clear_results = st.button("🗑️ Clear All Results", use_container_width=True, help="Reset context and outputs")
    st.markdown("---")
    st.markdown("### System Status")
    for agent, status in st.session_state['agent_status'].items():
        status_emoji = "✅" if status == "Completed" else "🔄" if status == "Running" else "❌"
        st.markdown(f"- {agent.replace('_', ' ').title()}: {status_emoji} {status}")
    if st.session_state['last_run']:
        st.markdown(f"\nLast run: {st.session_state['last_run']}")

# Handle clear results
if clear_results:
    st.session_state['context'] = {}
    st.session_state['agent_status'] = {
        'demand_forecast': 'Not Run',
        'production_schedule': 'Not Run',
        'component_sourcing': 'Not Run',
        'logistics': 'Not Run'
    }
    st.session_state['last_run'] = None
    st.session_state['agent_outputs'] = {}
    st.session_state['result_timestamps'] = {}
    st.success("🗑️ All results cleared!")
    st.rerun()

# Top-level handlers for sidebar agent runs (no dropdowns/expanders)
if run_pipeline:
    shared_context = {}
    # Step 1: Demand Forecasting
    try:
        forecast_agent = DemandForecastAgent(context=shared_context)
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
        forecast = forecast_agent.generate_demand_forecast(
            historical_sales, market_trends, seasonality, economic_data,
            customer_profiles, inventory, competition, feedback
        )
        shared_context['demand_forecast'] = forecast
        st.session_state['agent_outputs']['demand_forecast'] = parse_agent_output(forecast, 'demand_forecast')
    except Exception as e:
        st.error(f"❌ Pipeline error (forecast): {e}")
    # Step 2: Component Sourcing
    try:
        sourcing_agent = ComponentSourcingAgent(context=shared_context)
        requirements = sourcing_agent.extract_requirements_from_forecast(shared_context.get('demand_forecast', ''))
        sourcing_results = sourcing_agent.source_requirements(requirements)
        shared_context['sourcing_results'] = sourcing_results
        parsed_outputs = []
        for result in sourcing_results.values():
            if result:
                parsed_outputs.append(parse_agent_output(result, 'component_sourcing'))
        st.session_state['agent_outputs']['component_sourcing'] = parsed_outputs
    except Exception as e:
        st.error(f"❌ Pipeline error (sourcing): {e}")
    # Step 3: Production Scheduling
    try:
        scheduler = ProductionSchedulerAgent(context=shared_context)
        components = []
        for pn, data in shared_context.get('sourcing_results', {}).items():
            comp = (data or {}).get('component') or {}
            components.append({
                "part_number": pn,
                "lead_time": comp.get('lead_time', 14),
                "available_qty": comp.get('stock', 0)
            })
        stock_levels = {pn: (data.get('component') or {}).get('stock', 0) for pn, data in shared_context.get('sourcing_results', {}).items()}
        production_capacity = 200
        production_plan = scheduler.generate_production_plan(components, stock_levels, production_capacity)
        shared_context['production_schedule'] = production_plan
        st.session_state['agent_outputs']['production_schedule'] = parse_agent_output(production_plan, 'production_schedule')
    except Exception as e:
        st.error(f"❌ Pipeline error (production): {e}")
    # Step 4: Logistics Planning
    try:
        logistics_agent = LogisticsManagerAgent(context=shared_context)
        finished_goods = [
            {"part_number": "LM741", "quantity": 400, "destination": "Berlin"},
            {"part_number": "LM358", "quantity": 300, "destination": "New York"},
            {"part_number": "OP07", "quantity": 200, "destination": "Tokyo"}
        ]
        locations = {"Berlin": "Berlin Warehouse, Germany", "New York": "NYC Fulfillment Center, USA", "Tokyo": "Tokyo Logistics Hub, Japan"}
        timelines = {"LM741": "2025-08-20", "LM358": "2025-08-18", "OP07": "2025-08-25"}
        logistics_plan = logistics_agent.generate_logistics_plan(finished_goods, locations, timelines)
        shared_context['logistics_plan'] = logistics_plan
        st.session_state['agent_outputs']['logistics'] = parse_agent_output(logistics_plan, 'logistics')
    except Exception as e:
        st.error(f"❌ Pipeline error (logistics): {e}")
    # Finalize
    st.session_state['context'] = shared_context
    st.session_state['agent_status'] = {
        'demand_forecast': 'Completed',
        'production_schedule': 'Completed',
        'component_sourcing': 'Completed',
        'logistics': 'Completed',
    }
    st.session_state['last_run'] = time.strftime("%Y-%m-%d %H:%M:%S")
    st.success("🎉 Complete pipeline executed. View results in the tabs above.")
    st.rerun()

if run_forecast:
    clear_old_results()
    update_agent_status('demand_forecast', 'Running')
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
    try:
        forecast = forecast_agent.generate_demand_forecast(
            historical_sales, market_trends, seasonality, economic_data,
            customer_profiles, inventory, competition, feedback
        )
        context['demand_forecast'] = forecast
        parsed_output = parse_agent_output(forecast, 'demand_forecast')
        st.session_state['agent_outputs']['demand_forecast'] = parsed_output
        update_agent_status('demand_forecast', 'Completed')
    except Exception as e:
        st.error(f"❌ Error generating demand forecast: {str(e)}")
        update_agent_status('demand_forecast', 'Error')

if run_production:
    update_agent_status('production_schedule', 'Running')
    scheduler = ProductionSchedulerAgent(context=context)
    components = [
        {"part_number": "LM741", "lead_time": 14, "available_qty": 1200},
        {"part_number": "LM358", "lead_time": 10, "available_qty": 900},
        {"part_number": "OP07", "lead_time": 21, "available_qty": 500}
    ]
    stock_levels = {"LM741": 300, "LM358": 150, "OP07": 80}
    production_capacity = 1000
    try:
        schedule = scheduler.generate_production_plan(
            components, stock_levels, production_capacity=production_capacity
        )
        context['production_schedule'] = schedule
        parsed_output = parse_agent_output(schedule, 'production_schedule')
        st.session_state['agent_outputs']['production_schedule'] = parsed_output
        update_agent_status('production_schedule', 'Completed')
    except Exception as e:
        st.error(f"❌ Error generating production schedule: {str(e)}")
        update_agent_status('production_schedule', 'Error')

if run_sourcing:
    update_agent_status('component_sourcing', 'Running')
    sourcing_agent = ComponentSourcingAgent(context=context)
    try:
        sample_forecast = "Demand for LM741: 100 units, LM358: 80 units, OP07: 60 units"
        requirements = sourcing_agent.extract_requirements_from_forecast(sample_forecast)
        sourcing_results = sourcing_agent.source_requirements(requirements)
        context['sourcing_results'] = sourcing_results
        parsed_outputs = []
        for result in sourcing_results.values():
            if result:
                parsed_outputs.append(parse_agent_output(result, 'component_sourcing'))
        st.session_state['agent_outputs']['component_sourcing'] = parsed_outputs
        update_agent_status('component_sourcing', 'Completed')
    except Exception as e:
        st.error(f"❌ Error during component sourcing: {str(e)}")
        update_agent_status('component_sourcing', 'Error')

if run_logistics:
    update_agent_status('logistics', 'Running')
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
    try:
        plan = logistics_agent.generate_logistics_plan(finished_goods, locations, timelines)
        context['logistics_plan'] = plan
        parsed_output = parse_agent_output(plan, 'logistics')
        st.session_state['agent_outputs']['logistics'] = parsed_output
        update_agent_status('logistics', 'Completed')
    except Exception as e:
        st.error(f"❌ Error generating logistics plan: {str(e)}")
        update_agent_status('logistics', 'Error')

# Tabbed agent views (placed after handlers so results appear immediately)
tabs = st.tabs([
    "Agent 1: Demand Forecast",
    "Agent 2: Production Schedule",
    "Agent 3: Component Sourcing",
    "Agent 4: Logistics Plan",
])

with tabs[0]:
    status = st.session_state.get('agent_status', {}).get('demand_forecast', 'Not Run')
    st.subheader(f"Status: {status}")
    latest = st.session_state.get('context', {}).get('demand_forecast')
    if latest:
        tables = _extract_markdown_tables(latest)
        if tables:
            st.markdown("### 📋 Demand Forecast Table")
            for df in tables:
                st.table(df)
        else:
            st.markdown("### 📋 Latest Output")
            st.markdown('<div class="agent-output">', unsafe_allow_html=True)
            st.text(_sanitize_output_text(latest))
            st.markdown('</div>', unsafe_allow_html=True)
    parsed = st.session_state.get('agent_outputs', {}).get('demand_forecast')
    if parsed and parsed.get('extracted_data'):
        ed = parsed['extracted_data']
        rows = []
        for product, info in ed.items():
            if isinstance(info, dict):
                qtys = info.get('quantities', [])
                rows.append({"Product": product, "Quantity": max(qtys) if qtys else 0})
        if rows:
            df = pd.DataFrame(rows)
            fig = px.bar(df, x='Product', y='Quantity', title="Forecasted Mentions/Quantities", color_discrete_sequence=['#3498db'])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run Agent 1 to see results here.")

with tabs[1]:
    status = st.session_state.get('agent_status', {}).get('production_schedule', 'Not Run')
    st.subheader(f"Status: {status}")
    latest = st.session_state.get('context', {}).get('production_schedule')
    if latest:
        st.markdown("### 📋 Latest Output")
        st.markdown('<div class="agent-output">', unsafe_allow_html=True)
        st.text(latest)
        st.markdown('</div>', unsafe_allow_html=True)
    parsed = st.session_state.get('agent_outputs', {}).get('production_schedule')
    if parsed and parsed.get('extracted_data'):
        rows = []
        for product, info in parsed['extracted_data'].items():
            if isinstance(info, dict):
                pq = info.get('production_quantities', [])
                rows.append({"Product": product, "Production Quantity": max(pq) if pq else 0})
        rows = [r for r in rows if r["Production Quantity"] > 0]
        if rows:
            df = pd.DataFrame(rows)
            fig = px.bar(df, x='Product', y='Production Quantity', title="Production Quantities by Product", color_discrete_sequence=['#2ecc71'])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run Agent 2 to see results here.")

with tabs[2]:
    status = st.session_state.get('agent_status', {}).get('component_sourcing', 'Not Run')
    st.subheader(f"Status: {status}")
    sourcing_results = st.session_state.get('context', {}).get('sourcing_results')
    if sourcing_results:
        st.markdown("### 📋 Latest Output Summary")
        for pn, data in sourcing_results.items():
            comp = (data or {}).get('component') or {}
            risk = (data or {}).get('risk_report') or {}
            st.markdown(f"**Component: {pn}**")
            st.markdown('<div class="agent-output">', unsafe_allow_html=True)
            st.text(f"Requested Quantity: {data.get('requested_quantity', 0)}")
            st.text(f"Stock Available: {comp.get('stock', 0)}")
            st.text(f"Lead Time: {comp.get('lead_time', '-')} days")
            st.text(f"Price: ${comp.get('price', '-')}")
            if risk:
                st.text(f"Risk Score: {risk.get('risk_score', '-')}/10")
                st.text(f"Supplier Rating: {risk.get('supplier_rating', '-')}/10")
            st.markdown('</div>', unsafe_allow_html=True)
        rows = []
        for pn, data in sourcing_results.items():
            comp = (data or {}).get('component') or {}
            risk = (data or {}).get('risk_report') or {}
            rows.append({
                'Part Number': pn,
                'Price ($)': comp.get('price', 0),
                'Stock': comp.get('stock', 0),
                'Lead Time (days)': comp.get('lead_time', 0),
                'Risk Score': risk.get('risk_score', 0),
            })
        if rows:
            df = pd.DataFrame(rows)
            fig_risk = px.bar(df, x='Part Number', y='Risk Score', title="Component Risk Assessment", color='Risk Score', color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig_risk, use_container_width=True)
            fig_lt_price = px.scatter(df, x='Lead Time (days)', y='Price ($)', size='Stock', color='Risk Score', text='Part Number', title="Price vs Lead Time")
            st.plotly_chart(fig_lt_price, use_container_width=True)
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Run Agent 3 to see results here.")

with tabs[3]:
    status = st.session_state.get('agent_status', {}).get('logistics', 'Not Run')
    st.subheader(f"Status: {status}")
    latest = st.session_state.get('context', {}).get('logistics_plan')
    if latest:
        st.markdown("### 📋 Latest Output")
        st.markdown('<div class="agent-output">', unsafe_allow_html=True)
        st.text(latest)
        st.markdown('</div>', unsafe_allow_html=True)
    parsed = st.session_state.get('agent_outputs', {}).get('logistics')
    if parsed and parsed.get('extracted_data'):
        ed = parsed['extracted_data']
        destinations = [k for k, v in ed.items() if isinstance(v, dict) and v.get('mentioned')]
        if destinations:
            df = pd.DataFrame({'Destination': destinations, 'Shipments': [1] * len(destinations)})
            fig = px.pie(df, values='Shipments', names='Destination', title="Shipment Distribution by Destination")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run Agent 4 to see results here.")
# Full Orchestration Pipeline (Legacy - Not Used)
# This section is handled by the "Complete Pipeline Execution" expander below
if False:  # Disabled - run_all variable was undefined
    st.info("🚀 Running Full Orchestration Pipeline...")
    
    # Clear old results to ensure fresh data
    clear_old_results()
    
    # Initialize shared context for the complete pipeline
    shared_context = {}
    
    # Step 1: Demand Forecasting
    with st.spinner("📈 Step 1/4: Generating demand forecast..."):
        try:
            historical_sales = [
                {"product": "LM741", "region": "Europe", "sales": [100, 120, 130, 110]},
                {"product": "LM358", "region": "North America", "sales": [90, 95, 100, 105]},
                {"product": "OP07", "region": "Asia", "sales": [60, 70, 80, 75]},
            ]
            market_trends = {"Europe": "Stable", "North America": "Growing", "Asia": "Volatile"}
            seasonality = {"Q1": "Low", "Q2": "Medium", "Q3": "High", "Q4": "Medium"}
            economic_data = {"Europe": "Inflation 2%", "North America": "GDP growth 3%", "Asia": "Currency fluctuation"}
            customer_profiles = [
                {"customer_id": 1, "region": "Europe", "preferences": ["LM741", "OP07"]},
                {"customer_id": 2, "region": "North America", "preferences": ["LM358"]},
            ]
            inventory = {"LM741": 300, "LM358": 150, "OP07": 80}
            competition = {"LM741": 2.50, "LM358": 2.40, "OP07": 2.60}
            feedback = [
                "LM741 is reliable but sometimes out of stock.",
                "LM358 price is competitive.",
                "OP07 needs better documentation.",
            ]
            
            forecast_agent = DemandForecastAgent(context=shared_context)
            forecast_report = forecast_agent.generate_demand_forecast(
                historical_sales, market_trends, seasonality, economic_data,
                customer_profiles, inventory, competition, feedback
            )
            shared_context["demand_forecast"] = forecast_report
            context["demand_forecast"] = forecast_report
            
            st.success("✅ Demand forecast completed!")
            update_agent_status('demand_forecast', 'Completed')
            
        except Exception as e:
            st.error(f"❌ Error in demand forecasting: {e}")
            update_agent_status('demand_forecast', 'Error')
            st.stop()
    
    # Step 2: Component Sourcing
    with st.spinner("🔍 Step 2/4: Sourcing components..."):
        try:
            sourcing_agent = ComponentSourcingAgent(context=shared_context)
            requirements = sourcing_agent.extract_requirements_from_forecast(forecast_report)
            sourcing_results = sourcing_agent.source_requirements(requirements)
            shared_context["sourcing_results"] = sourcing_results
            context["sourcing_results"] = sourcing_results
            
            st.success("✅ Component sourcing completed!")
            update_agent_status('component_sourcing', 'Completed')
            
        except Exception as e:
            st.error(f"❌ Error in component sourcing: {e}")
            update_agent_status('component_sourcing', 'Error')
            st.stop()
    
    # Step 3: Production Scheduling
    with st.spinner("🏭 Step 3/4: Generating production plan..."):
        try:
            # Build components list for scheduler from sourcing results
            components = []
            for pn, data in sourcing_results.items():
                comp = data.get("component") or {}
                components.append({
                    "part_number": pn,
                    "lead_time": comp.get("lead_time", 14),
                    "available_qty": comp.get("stock", 0)
                })
            stock_levels = {pn: (data.get("component") or {}).get("stock", 0) for pn, data in sourcing_results.items()}
            production_capacity = 200
            
            scheduler = ProductionSchedulerAgent(context=shared_context)
            production_plan = scheduler.generate_production_plan(components, stock_levels, production_capacity)
            shared_context["production_plan"] = production_plan
            context["production_schedule"] = production_plan
            
            st.success("✅ Production plan completed!")
            update_agent_status('production_schedule', 'Completed')
            
        except Exception as e:
            st.error(f"❌ Error in production scheduling: {e}")
            update_agent_status('production_schedule', 'Error')
            st.stop()
    
    # Step 4: Logistics Planning
    with st.spinner("🚚 Step 4/4: Planning logistics..."):
        try:
            finished_goods = [
                {"part_number": "LM741", "quantity": 400, "destination": "Berlin"},
                {"part_number": "LM358", "quantity": 300, "destination": "New York"},
                {"part_number": "OP07", "quantity": 200, "destination": "Tokyo"},
            ]
            locations = {
                "Berlin": "Berlin Warehouse, Germany",
                "New York": "NYC Fulfillment Center, USA",
                "Tokyo": "Tokyo Logistics Hub, Japan",
            }
            timelines = {"LM741": "2025-08-20", "LM358": "2025-08-18", "OP07": "2025-08-25"}
            
            logistics_agent = LogisticsManagerAgent(context=shared_context)
            logistics_plan = logistics_agent.generate_logistics_plan(finished_goods, locations, timelines)
            shared_context["logistics_plan"] = logistics_plan
            context["logistics_plan"] = logistics_plan
            
            st.success("✅ Logistics plan completed!")
            update_agent_status('logistics', 'Completed')
            
        except Exception as e:
            st.error(f"❌ Error in logistics planning: {e}")
            update_agent_status('logistics', 'Error')
            st.stop()
    
    # Pipeline Summary
    st.success("🎉 Full Orchestration Pipeline completed successfully!")
    st.markdown("### 📋 Pipeline Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Demand Forecast", "✅ Completed")
    with col2:
        st.metric("Component Sourcing", f"✅ {len(sourcing_results)} components")
    with col3:
        st.metric("Production Plan", "✅ Generated")
    with col4:
        st.metric("Logistics Plan", "✅ Optimized")
    
    # Update session state
    st.session_state['context'] = shared_context
    st.session_state['last_run'] = time.strftime("%Y-%m-%d %H:%M:%S")
    st.rerun()


 # Complete pipeline demo removed to avoid verbose outputs in Agent 1 view

# System Overview
with st.expander("🔍 System Overview & Agent Interactions", expanded=False):
    st.markdown("### 🤖 Agent Status Summary")
    
    # Create a status overview
    status_data = []
    for agent, status in st.session_state['agent_status'].items():
        status_data.append({
            'Agent': agent.replace('_', ' ').title(),
            'Status': status,
            'Last Run': st.session_state['last_run'] if status != 'Not Run' else 'Never'
        })
    
    if status_data:
        df_status = pd.DataFrame(status_data)
        st.dataframe(df_status, use_container_width=True)
    
    # Show agent outputs summary
    if st.session_state['agent_outputs']:
        st.markdown("### 📊 Agent Outputs Summary")
        for agent, output in st.session_state['agent_outputs'].items():
            if output:
                st.markdown(f"**{agent.replace('_', ' ').title()}**")
                if isinstance(output, list):
                    st.text(f"Generated {len(output)} results")
                else:
                    st.text("Output generated successfully")
                st.markdown("---")

# Context viewer
with st.expander("🔎 Shared Context (Memory)", expanded=False):
    st.json(context)
