from agent import LogisticsManagerAgent

if __name__ == "__main__":
    # Example data for demo
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

    logistics_agent = LogisticsManagerAgent()
    plan = logistics_agent.generate_logistics_plan(finished_goods, locations, timelines)
    print("\n--- Optimized Shipment Plan & Warehouse Allocation ---\n")
    print(plan)
