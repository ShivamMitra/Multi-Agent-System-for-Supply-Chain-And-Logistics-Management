from agent import DemandForecastAgent

if __name__ == "__main__":
    # Example data for demo
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

    forecast_agent = DemandForecastAgent()
    report = forecast_agent.generate_demand_forecast(
        historical_sales, market_trends, seasonality, economic_data,
        customer_profiles, inventory, competition, feedback
    )
    print("\n--- Demand Forecast Report & Suggested Actions ---\n")
    print(report)
