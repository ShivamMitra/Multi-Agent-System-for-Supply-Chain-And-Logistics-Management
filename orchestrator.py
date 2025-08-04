import logging
from agent import (
    ElectronicComponentAgent,
    ProductionSchedulerAgent,
    LogisticsManagerAgent,
    DemandForecastAgent
)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Agent 4: Market & Customer Demand Forecasting
def agent4_forecast_demand():
    forecast_agent = DemandForecastAgent()
    # Example input data (could be loaded from files/db in real use)
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
    logging.info("Agent 4: Forecasting demand...")
    forecast = forecast_agent.generate_demand_forecast(
        historical_sales, market_trends, seasonality, economic_data,
        customer_profiles, inventory, competition, feedback
    )
    logging.info(f"Agent 4 Output: {forecast}")
    return forecast

# Agent 2: Production & Inventory Optimization
def agent2_schedule_production(demand_forecast):
    scheduler = ProductionSchedulerAgent()
    # Example: parse demand forecast to get production needs (simplified for demo)
    components = [
        {"part_number": "LM741", "lead_time": 14, "available_qty": 1200},
        {"part_number": "LM358", "lead_time": 10, "available_qty": 900},
        {"part_number": "OP07", "lead_time": 21, "available_qty": 500}
    ]
    stock_levels = {"LM741": 300, "LM358": 150, "OP07": 80}
    production_capacity = 200
    logging.info("Agent 2: Scheduling production based on demand forecast...")
    plan = scheduler.generate_production_plan(components, stock_levels, production_capacity)
    logging.info(f"Agent 2 Output: {plan}")
    return plan

# Agent 1: Component Sourcing & Risk Management
def agent1_source_components(production_plan):
    sourcing_agent = ElectronicComponentAgent()
    # Example: parse production plan to get required components (simplified for demo)
    part_numbers = ["LM741", "LM358", "OP07"]
    sourced = []
    for pn in part_numbers:
        comp = sourcing_agent.source_component(pn, quantity=200)
        if comp:
            sourced.append(f"{pn}: sourced {comp.stock} units, risk score {comp.risk_score}")
    delivery_plan = "; ".join(sourced)
    logging.info("Agent 1: Sourcing components based on production plan...")
    logging.info(f"Agent 1 Output: {delivery_plan}")
    return delivery_plan

# Agent 3: Global Logistics & Fulfillment
def agent3_manage_logistics(delivery_plan):
    logistics_agent = LogisticsManagerAgent()
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
    logging.info("Agent 3: Managing logistics and fulfillment...")
    plan = logistics_agent.generate_logistics_plan(finished_goods, locations, timelines)
    logging.info(f"Agent 3 Output: {plan}")
    return plan

# Orchestrator main function
def main():
    logging.info("--- Multi-Agent Supply Chain Orchestration Started ---")
    demand = agent4_forecast_demand()
    production = agent2_schedule_production(demand)
    sourcing = agent1_source_components(production)
    logistics = agent3_manage_logistics(sourcing)
    logging.info("--- Orchestration Complete ---")
    print("\nFinal Logistics Plan:\n", logistics)

if __name__ == "__main__":
    main()
