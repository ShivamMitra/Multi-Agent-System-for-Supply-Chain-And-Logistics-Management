from agent import ProductionSchedulerAgent

if __name__ == "__main__":
    # Example data for demo
    components = [
        {"part_number": "LM741", "lead_time": 14, "available_qty": 1200},
        {"part_number": "LM358", "lead_time": 10, "available_qty": 900},
        {"part_number": "OP07", "lead_time": 21, "available_qty": 500}
    ]
    stock_levels = {"LM741": 300, "LM358": 150, "OP07": 80}
    production_capacity = 200

    # Shared context for memory
    shared_context = {}
    scheduler = ProductionSchedulerAgent(context=shared_context)
    plan = scheduler.generate_production_plan(components, stock_levels, production_capacity)
    # Store the plan in context for future agent use
    shared_context['production_plan'] = plan
    print("\n--- Final Production Plan ---\n")
    print(plan)
    print("\n--- Context Memory ---\n")
    print(shared_context)
