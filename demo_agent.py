#!/usr/bin/env python3
"""
End-to-end MAS demo:
1) DemandForecastAgent → demand report
2) ComponentSourcingAgent → extract requirements, source parts + risks
3) ProductionSchedulerAgent → production plan
4) LogisticsManagerAgent → logistics plan
All agents share a context and are initialized in sequence.
"""

import os
import json
from dotenv import load_dotenv
from agent import (
    DemandForecastAgent,
    ComponentSourcingAgent,
    ProductionSchedulerAgent,
    LogisticsManagerAgent,
)

# Load environment variables
load_dotenv()

def demo_pipeline():
    print("🔧 MAS End-to-End Demo")
    print("=" * 40)

    shared_context = {}

    # 1) Demand forecasting
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
    print("\n--- Demand Forecast Report ---\n")
    print(forecast_report)

    # 2) Component sourcing from forecast
    sourcing_agent = ComponentSourcingAgent(context=shared_context)
    requirements = sourcing_agent.extract_requirements_from_forecast(forecast_report)
    sourcing_results = sourcing_agent.source_requirements(requirements)
    print("\n--- Sourcing Results ---\n")
    if not sourcing_results:
        print("No sourcing requirements identified from the forecast.")
    else:
        for pn, data in sourcing_results.items():
            comp = data.get("component") or {}
            risk = data.get("risk_report") or {}
            print(f"- {pn} | requested: {data.get('requested_quantity', 0)} | stock: {comp.get('stock', 0)} | lead_time: {comp.get('lead_time', '-')} days | price: {comp.get('price', '-')}")
            if risk:
                print(f"  risk_score: {risk.get('risk_score', '-')}, supplier_rating: {risk.get('supplier_rating', '-')}")
                if risk.get('risk_factors'):
                    print(f"  risk_factors: {', '.join(risk.get('risk_factors'))}")
                if risk.get('mitigation_strategies'):
                    print(f"  mitigation: {', '.join(risk.get('mitigation_strategies'))}")

    # 3) Production scheduling
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
    print("\n--- Production Plan ---\n")
    print(production_plan)

    # 4) Logistics planning based on production output (mock shipment quantities)
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
    print("\n--- Logistics Plan ---\n")
    print(logistics_plan)

    # Omit raw JSON context to keep output readable

if __name__ == "__main__":
    demo_pipeline()