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

# Function to update status
def update_agent_status(agent, status):
    st.session_state['agent_status'][agent] = status
    st.session_state['last_run'] = time.strftime("%Y-%m-%d %H:%M:%S")
    if status == 'Completed':
        st.session_state['result_timestamps'][agent] = time.time()
    st.rerun()

# Function to clear old results when new ones are generated
def clear_old_results():
    """Clear old results to ensure fresh data is displayed"""
    if 'agent_outputs' in st.session_state:
        st.session_state['agent_outputs'] = {}

# Sidebar controls
with st.sidebar:
    st.title("🛠️ Controls")
    run_all = st.button("🚀 Run Full Orchestration", use_container_width=True)
    
    st.markdown("### Individual Agents")
    col1, col2 = st.columns(2)
    with col1:
        run_forecast = st.button("📈 Forecast Demand")
        run_production = st.button("🏭 Schedule Production")
    with col2:
        run_sourcing = st.button("🔍 Source Components")
        run_logistics = st.button("🚚 Plan Logistics")
    
    st.markdown("### Pipeline Options")
    run_pipeline = st.button("🔄 Run Complete Pipeline", use_container_width=True)
    
    st.markdown("### Data Management")
    clear_results = st.button("🗑️ Clear All Results", use_container_width=True)
    
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

# Full Orchestration Pipeline
if run_all and not run_pipeline:
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

# Agent 1: Demand Forecasting
with st.expander("📊 Agent 1: Market & Demand Forecasting", expanded=True):
    if st.button("▶️ Run Demand Forecast", key="forecast") or run_forecast or (run_all and not run_pipeline):
        # Clear old results when running fresh
        if not (run_all and not run_pipeline):
            clear_old_results()
        update_agent_status('demand_forecast', 'Running')
        forecast_agent = DemandForecastAgent(context=context)
        
        # Sample data - in a real app, this would come from a database or API
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
        
        with st.spinner("🔍 Analyzing market trends and forecasting demand..."):
            try:
                forecast = forecast_agent.generate_demand_forecast(
                    historical_sales, market_trends, seasonality, economic_data,
                    customer_profiles, inventory, competition, feedback
                )
                context['demand_forecast'] = forecast
                
                # Parse the output for visualization
                parsed_output = parse_agent_output(forecast, 'demand_forecast')
                st.session_state['agent_outputs']['demand_forecast'] = parsed_output
                
                # Display results
                st.success("✅ Demand forecast generated successfully!")
                
                # Display the actual agent output
                st.markdown("### 📋 Agent Output")
                st.markdown('<div class="agent-output">', unsafe_allow_html=True)
                st.text(forecast)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Create visualizations based on parsed data
                if parsed_output and parsed_output['extracted_data']:
                    st.markdown("### 📊 Extracted Insights")
                    
                    # Create a simple visualization of mentioned products
                    products = list(parsed_output['extracted_data'].keys())
                    if products:
                        mentioned_data = {
                            'Product': products,
                            'Mentioned': [True] * len(products)
                        }
                        df = pd.DataFrame(mentioned_data)
                        
                        fig = px.bar(df, x='Product', y='Mentioned', 
                                    title="Products Mentioned in Forecast",
                                    color_discrete_sequence=['#3498db'])
                        st.plotly_chart(fig, use_container_width=True)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Products Analyzed", len(historical_sales))
                with col2:
                    st.metric("Regions Covered", len(market_trends))
                with col3:
                    st.metric("Customer Profiles", len(customer_profiles))
                
                update_agent_status('demand_forecast', 'Completed')
                
            except Exception as e:
                st.error(f"❌ Error generating demand forecast: {str(e)}")
                update_agent_status('demand_forecast', 'Error')
    elif 'demand_forecast' in context:
        # Check if this is a fresh result from the current session
        if st.session_state.get('agent_status', {}).get('demand_forecast') == 'Completed':
            st.success("✅ Using recently generated forecast")
        else:
            st.info("ℹ️ Using previously generated forecast. Click 'Run Demand Forecast' to update.")
        
        forecast = context['demand_forecast']
        
        # Display the actual agent output
        st.markdown("### 📋 Agent Output")
        st.markdown('<div class="agent-output">', unsafe_allow_html=True)
        st.text(forecast)
        st.markdown('</div>', unsafe_allow_html=True)

# Agent 2: Production Scheduling
with st.expander("🏭 Agent 2: Production & Inventory Optimization", expanded=True):
    if st.button("⚙️ Generate Production Schedule", key="production") or run_production or (run_all and not run_pipeline):
        update_agent_status('production_schedule', 'Running')
        scheduler = ProductionSchedulerAgent(context=context)
        
        # Sample data - in a real app, this would come from a database or API
        components = [
            {"part_number": "LM741", "lead_time": 14, "available_qty": 1200},
            {"part_number": "LM358", "lead_time": 10, "available_qty": 900},
            {"part_number": "OP07", "lead_time": 21, "available_qty": 500}
        ]
        stock_levels = {"LM741": 300, "LM358": 150, "OP07": 80}
        production_capacity = 1000
        
        with st.spinner("🔄 Optimizing production schedule..."):
            try:
                schedule = scheduler.generate_production_plan(
                    components, stock_levels, production_capacity=production_capacity
                )
                context['production_schedule'] = schedule
                
                # Parse the output for visualization
                parsed_output = parse_agent_output(schedule, 'production_schedule')
                st.session_state['agent_outputs']['production_schedule'] = parsed_output
                
                # Display results
                st.success("✅ Production schedule generated successfully!")
                
                # Display the actual agent output
                st.markdown("### 📋 Agent Output")
                st.markdown('<div class="agent-output">', unsafe_allow_html=True)
                st.text(schedule)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Create visualizations based on parsed data
                if parsed_output and parsed_output['extracted_data']:
                    st.markdown("### 📊 Extracted Insights")
                    
                    # Create a visualization of production quantities
                    products = list(parsed_output['extracted_data'].keys())
                    if products:
                        production_data = []
                        for product in products:
                            data = parsed_output['extracted_data'][product]
                            if 'production_quantities' in data and data['production_quantities']:
                                production_data.append({
                                    'Product': product,
                                    'Production Quantity': max(data['production_quantities'])
                                })
                        
                        if production_data:
                            df = pd.DataFrame(production_data)
                            fig = px.bar(df, x='Product', y='Production Quantity',
                                        title="Production Quantities by Product",
                                        color_discrete_sequence=['#2ecc71'])
                            st.plotly_chart(fig, use_container_width=True)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Components Analyzed", len(components))
                with col2:
                    st.metric("Production Capacity", production_capacity)
                with col3:
                    st.metric("Total Current Stock", sum(stock_levels.values()))
                
                update_agent_status('production_schedule', 'Completed')
                
            except Exception as e:
                st.error(f"❌ Error generating production schedule: {str(e)}")
                update_agent_status('production_schedule', 'Error')
    elif 'production_schedule' in context:
        # Check if this is a fresh result from the current session
        if st.session_state.get('agent_status', {}).get('production_schedule') == 'Completed':
            st.success("✅ Using recently generated production schedule")
        else:
            st.info("ℹ️ Using previously generated production schedule. Click 'Generate Production Schedule' to update.")
        
        schedule = context['production_schedule']
        
        # Display the actual agent output
        st.markdown("### 📋 Agent Output")
        st.markdown('<div class="agent-output">', unsafe_allow_html=True)
        st.text(schedule)
        st.markdown('</div>', unsafe_allow_html=True)

# Agent 3: Component Sourcing
with st.expander("🔍 Agent 3: Component Sourcing & Risk Management", expanded=True):
    if st.button("🔄 Source Components", key="sourcing") or run_sourcing or (run_all and not run_pipeline):
        update_agent_status('component_sourcing', 'Running')
        sourcing_agent = ComponentSourcingAgent(context=context)
        
        with st.spinner("🔎 Sourcing components and assessing risks..."):
            try:
                # Use a sample forecast to extract requirements
                sample_forecast = "Demand for LM741: 100 units, LM358: 80 units, OP07: 60 units"
                requirements = sourcing_agent.extract_requirements_from_forecast(sample_forecast)
                sourcing_results = sourcing_agent.source_requirements(requirements)
                
                context['sourcing_results'] = sourcing_results
                
                # Parse the output for visualization
                parsed_outputs = []
                for result in sourcing_results:
                    if result:
                        parsed_output = parse_agent_output(result, 'component_sourcing')
                        parsed_outputs.append(parsed_output)
                
                st.session_state['agent_outputs']['component_sourcing'] = parsed_outputs
                
                # Display results
                st.success("✅ Component sourcing complete!")
                
                # Display the actual agent outputs
                st.markdown("### 📋 Agent Outputs")
                if not sourcing_results:
                    st.warning("No sourcing requirements identified.")
                else:
                    for pn, data in sourcing_results.items():
                        comp = data.get("component") or {}
                        risk = data.get("risk_report") or {}
                        
                        st.markdown(f"**Component: {pn}**")
                        st.markdown('<div class="agent-output">', unsafe_allow_html=True)
                        st.text(f"Requested Quantity: {data.get('requested_quantity', 0)}")
                        st.text(f"Stock Available: {comp.get('stock', 0)}")
                        st.text(f"Lead Time: {comp.get('lead_time', '-')} days")
                        st.text(f"Price: ${comp.get('price', '-')}")
                        if risk:
                            st.text(f"Risk Score: {risk.get('risk_score', '-')}/10")
                            st.text(f"Supplier Rating: {risk.get('supplier_rating', '-')}/10")
                            if risk.get('risk_factors'):
                                st.text(f"Risk Factors: {', '.join(risk.get('risk_factors'))}")
                            if risk.get('mitigation_strategies'):
                                st.text(f"Mitigation: {', '.join(risk.get('mitigation_strategies'))}")
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Create visualizations based on parsed data
                if parsed_outputs:
                    st.markdown("### 📊 Component Analysis")
                    
                    # Prepare data for visualization
                    sourcing_data = []
                    for pn, data in sourcing_results.items():
                        comp = data.get("component") or {}
                        risk = data.get("risk_report") or {}
                        sourcing_data.append({
                            'Part Number': pn,
                            'Price ($)': comp.get('price', 0),
                            'Stock': comp.get('stock', 0),
                            'Lead Time (days)': comp.get('lead_time', 0),
                            'Risk Score': risk.get('risk_score', 0)
                        })
                    
                    if sourcing_data:
                        df = pd.DataFrame(sourcing_data)
                        
                        # Risk distribution chart
                        fig_risk = px.bar(df, x='Part Number', y='Risk Score',
                                        title="Component Risk Assessment",
                                        color='Risk Score',
                                        color_continuous_scale='RdYlGn_r')
                        st.plotly_chart(fig_risk, use_container_width=True)
                        
                        # Price vs Lead Time scatter plot
                        fig_sourcing = px.scatter(df, 
                                               x='Lead Time (days)', 
                                               y='Price ($)',
                                               size='Stock',
                                               color='Risk Score',
                                               text='Part Number',
                                               title="Price vs Lead Time Analysis")
                        st.plotly_chart(fig_sourcing, use_container_width=True)
                        
                        # Display sourcing details
                        st.subheader("Component Sourcing Details")
                        st.dataframe(df, use_container_width=True)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Components Sourced", len(sourcing_results))
                with col2:
                    risk_scores = [data.get("risk_report", {}).get("risk_score", 0) for data in sourcing_results.values()]
                    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
                    st.metric("Average Risk Score", f"{avg_risk:.1f}/10")
                with col3:
                    total_stock = sum(data.get("component", {}).get("stock", 0) for data in sourcing_results.values())
                    st.metric("Total Available Stock", total_stock)
                
                update_agent_status('component_sourcing', 'Completed')
                
            except Exception as e:
                st.error(f"❌ Error during component sourcing: {str(e)}")
                update_agent_status('component_sourcing', 'Error')
    elif 'sourcing_results' in context:
        # Check if this is a fresh result from the current session
        if st.session_state.get('agent_status', {}).get('component_sourcing') == 'Completed':
            st.success("✅ Using recently sourced components")
        else:
            st.info("ℹ️ Using previously sourced components. Click 'Source Components' to update.")
        
        sourcing_results = context['sourcing_results']
        
        # Display the actual agent outputs
        st.markdown("### 📋 Agent Outputs")
        if not sourcing_results:
            st.warning("No sourcing requirements identified.")
        else:
            for pn, data in sourcing_results.items():
                comp = data.get("component") or {}
                risk = data.get("risk_report") or {}
                
                st.markdown(f"**Component: {pn}**")
                st.markdown('<div class="agent-output">', unsafe_allow_html=True)
                st.text(f"Requested Quantity: {data.get('requested_quantity', 0)}")
                st.text(f"Stock Available: {comp.get('stock', 0)}")
                st.text(f"Lead Time: {comp.get('lead_time', '-')} days")
                st.text(f"Price: ${comp.get('price', '-')}")
                if risk:
                    st.text(f"Risk Score: {risk.get('risk_score', '-')}/10")
                    st.text(f"Supplier Rating: {risk.get('supplier_rating', '-')}/10")
                    if risk.get('risk_factors'):
                        st.text(f"Risk Factors: {', '.join(risk.get('risk_factors'))}")
                    if risk.get('mitigation_strategies'):
                        st.text(f"Mitigation: {', '.join(risk.get('mitigation_strategies'))}")
                st.markdown('</div>', unsafe_allow_html=True)

# Agent 4: Logistics
with st.expander("🚚 Agent 4: Global Logistics & Fulfillment", expanded=True):
    if st.button("🚚 Plan Logistics", key="logistics") or run_logistics or (run_all and not run_pipeline):
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
        
        with st.spinner("🚚 Planning logistics..."):
            try:
                plan = logistics_agent.generate_logistics_plan(finished_goods, locations, timelines)
                context['logistics_plan'] = plan
                
                # Parse the output for visualization
                parsed_output = parse_agent_output(plan, 'logistics')
                st.session_state['agent_outputs']['logistics'] = parsed_output
                
                # Display results
                st.success("✅ Logistics plan generated successfully!")
                
                # Display the actual agent output
                st.markdown("### 📋 Agent Output")
                st.markdown('<div class="agent-output">', unsafe_allow_html=True)
                st.text(plan)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Create visualizations based on parsed data
                if parsed_output and parsed_output['extracted_data']:
                    st.markdown("### 📊 Logistics Analysis")
                    
                    # Create a visualization of destinations
                    destinations = [k for k, v in parsed_output['extracted_data'].items() if isinstance(v, dict) and v.get('mentioned')]
                    if destinations:
                        dest_data = {
                            'Destination': destinations,
                            'Shipments': [1] * len(destinations)
                        }
                        df = pd.DataFrame(dest_data)
                        
                        fig = px.pie(df, values='Shipments', names='Destination',
                                    title="Shipment Distribution by Destination")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Shipments", len(finished_goods))
                with col2:
                    st.metric("Destinations", len(locations))
                with col3:
                    total_quantity = sum(item['quantity'] for item in finished_goods)
                    st.metric("Total Quantity", total_quantity)
                
                update_agent_status('logistics', 'Completed')
                
            except Exception as e:
                st.error(f"❌ Error generating logistics plan: {str(e)}")
                update_agent_status('logistics', 'Error')
    elif 'logistics_plan' in context:
        # Check if this is a fresh result from the current session
        if st.session_state.get('agent_status', {}).get('logistics') == 'Completed':
            st.success("✅ Using recently generated logistics plan")
        else:
            st.info("ℹ️ Using previously generated logistics plan. Click 'Plan Logistics' to update.")
        
        plan = context['logistics_plan']
        
        # Display the actual agent output
        st.markdown("### 📋 Agent Output")
        st.markdown('<div class="agent-output">', unsafe_allow_html=True)
        st.text(plan)
        st.markdown('</div>', unsafe_allow_html=True)

# Complete Pipeline Execution
with st.expander("🔄 Complete Pipeline Execution (demo_agent.py)", expanded=False):
    if st.button("🚀 Execute Complete Pipeline", key="pipeline") or run_pipeline:
        st.info("🔄 Running complete pipeline from demo_agent.py...")
        
        # Initialize shared context
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
                
                st.success("✅ Demand forecast completed!")
                st.markdown("### 📊 Demand Forecast Results")
                st.markdown('<div class="agent-output">', unsafe_allow_html=True)
                st.text(forecast_report)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error in demand forecasting: {e}")
                st.stop()
        
        # Step 2: Component Sourcing
        with st.spinner("🔍 Step 2/4: Sourcing components..."):
            try:
                sourcing_agent = ComponentSourcingAgent(context=shared_context)
                requirements = sourcing_agent.extract_requirements_from_forecast(forecast_report)
                sourcing_results = sourcing_agent.source_requirements(requirements)
                
                st.success("✅ Component sourcing completed!")
                st.markdown("### 🔍 Component Sourcing Results")
                
                if not sourcing_results:
                    st.warning("No sourcing requirements identified from the forecast.")
                else:
                    for pn, data in sourcing_results.items():
                        comp = data.get("component") or {}
                        risk = data.get("risk_report") or {}
                        
                        st.markdown(f"**Component: {pn}**")
                        st.markdown('<div class="agent-output">', unsafe_allow_html=True)
                        st.text(f"Requested Quantity: {data.get('requested_quantity', 0)}")
                        st.text(f"Stock Available: {comp.get('stock', 0)}")
                        st.text(f"Lead Time: {comp.get('lead_time', '-')} days")
                        st.text(f"Price: ${comp.get('price', '-')}")
                        if risk:
                            st.text(f"Risk Score: {risk.get('risk_score', '-')}/10")
                            st.text(f"Supplier Rating: {risk.get('supplier_rating', '-')}/10")
                            if risk.get('risk_factors'):
                                st.text(f"Risk Factors: {', '.join(risk.get('risk_factors'))}")
                            if risk.get('mitigation_strategies'):
                                st.text(f"Mitigation: {', '.join(risk.get('mitigation_strategies'))}")
                        st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error in component sourcing: {e}")
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
                
                st.success("✅ Production plan completed!")
                st.markdown("### 🏭 Production Plan Results")
                st.markdown('<div class="agent-output">', unsafe_allow_html=True)
                st.text(production_plan)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error in production scheduling: {e}")
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
                
                st.success("✅ Logistics plan completed!")
                st.markdown("### 🚚 Logistics Plan Results")
                st.markdown('<div class="agent-output">', unsafe_allow_html=True)
                st.text(logistics_plan)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error in logistics planning: {e}")
                st.stop()
        
        # Pipeline Summary
        st.success("🎉 Complete pipeline executed successfully!")
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
        st.session_state['agent_status'] = {
            'demand_forecast': 'Completed',
            'production_schedule': 'Completed',
            'component_sourcing': 'Completed',
            'logistics': 'Completed'
        }
        st.session_state['last_run'] = time.strftime("%Y-%m-%d %H:%M:%S")

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