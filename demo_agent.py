#!/usr/bin/env python3
"""
Electronic Component Agent Demo
Demonstrates the agent's capabilities with real examples
"""

import json
import time
from agent import ElectronicComponentAgent

def demo_single_component():
    """Demo single component sourcing"""
    print("🔍 Demo: Single Component Sourcing")
    print("=" * 40)
    
    agent = ElectronicComponentAgent()
    
    # Test different types of components
    components = [
        ("LM741", "Operational Amplifier"),
        ("NE555", "Timer IC"),
        ("LM7805", "Voltage Regulator"),
        ("LM358", "Dual Op-Amp")
    ]
    
    for part_number, description in components:
        print(f"\n📦 Sourcing: {part_number} ({description})")
        
        start_time = time.time()
        component = agent.source_component(part_number, quantity=100)
        end_time = time.time()
        
        if component:
            print(f"✅ Found: {component.manufacturer}")
            print(f"   Price: ${component.price:.2f}")
            print(f"   Stock: {component.stock} units")
            print(f"   Lead Time: {component.lead_time} days")
            print(f"   Risk Score: {component.risk_score:.2f}/10")
            print(f"   Response Time: {(end_time - start_time):.3f}s")
            
            # Get detailed risk report
            risk_report = agent.get_risk_report(part_number)
            if risk_report:
                print(f"   Risk Factors: {', '.join(risk_report['risk_factors'][:3])}")
                print(f"   Mitigation: {', '.join(risk_report['mitigation_strategies'][:2])}")
        else:
            print(f"❌ Failed to source {part_number}")

def demo_risk_assessment():
    """Demo risk assessment capabilities"""
    print("\n⚠️ Demo: Risk Assessment Analysis")
    print("=" * 40)
    
    agent = ElectronicComponentAgent()
    
    # Test components with different risk profiles
    high_risk_components = ["LM741", "NE555"]  # Common components
    medium_risk_components = ["AD822", "TL072"]  # Specialized components
    
    print("\n🔴 High-Risk Components:")
    for component in high_risk_components:
        comp = agent.source_component(component)
        if comp:
            risk_report = agent.get_risk_report(component)
            if risk_report:
                print(f"  {component}: Risk Score {risk_report['risk_score']:.2f}")
                print(f"    Factors: {', '.join(risk_report['risk_factors'])}")
                print(f"    Strategies: {', '.join(risk_report['mitigation_strategies'])}")
    
    print("\n🟡 Medium-Risk Components:")
    for component in medium_risk_components:
        comp = agent.source_component(component)
        if comp:
            risk_report = agent.get_risk_report(component)
            if risk_report:
                print(f"  {component}: Risk Score {risk_report['risk_score']:.2f}")
                print(f"    Factors: {', '.join(risk_report['risk_factors'])}")
                print(f"    Strategies: {', '.join(risk_report['mitigation_strategies'])}")

def demo_sourcing_optimization():
    """Demo sourcing optimization"""
    print("\n🎯 Demo: Sourcing Optimization")
    print("=" * 40)
    
    agent = ElectronicComponentAgent()
    
    # Different optimization scenarios
    scenarios = [
        {
            "name": "Basic Circuit Components",
            "components": ["LM741", "LM358", "NE555"]
        },
        {
            "name": "Power Supply Components", 
            "components": ["LM7805", "LM317", "LM1117"]
        },
        {
            "name": "Audio Circuit Components",
            "components": ["LM386", "TL072", "LM324"]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🔧 Scenario: {scenario['name']}")
        print(f"   Components: {', '.join(scenario['components'])}")
        
        start_time = time.time()
        optimization = agent.optimize_sourcing(scenario['components'])
        end_time = time.time()
        
        if 'error' not in optimization:
            print(f"   ⚡ Response Time: {(end_time - start_time):.3f}s")
            print(f"   📋 Recommended Suppliers: {', '.join(optimization.get('recommended_suppliers', []))}")
            print(f"   💰 Cost Optimization: {', '.join(optimization.get('cost_optimization', []))}")
            print(f"   🛡️ Risk Mitigation: {', '.join(optimization.get('risk_mitigation', []))}")
            print(f"   ⏱️ Timeline: {optimization.get('timeline', 'N/A')}")
        else:
            print(f"   ❌ Optimization failed")

def demo_performance_comparison():
    """Demo performance comparison"""
    print("\n⚡ Demo: Performance Comparison")
    print("=" * 40)
    
    agent = ElectronicComponentAgent()
    
    # Test response times for different component types
    test_components = [
        ("LM741", "Common Op-Amp"),
        ("AD822", "Precision Op-Amp"), 
        ("NE555", "Timer IC"),
        ("LM7805", "Voltage Regulator")
    ]
    
    performance_data = []
    
    for part_number, description in test_components:
        print(f"\n🔍 Testing: {part_number} ({description})")
        
        times = []
        for i in range(3):  # Test 3 times
            start_time = time.time()
            component = agent.source_component(part_number)
            end_time = time.time()
            times.append(end_time - start_time)
            
            if component:
                print(f"   Run {i+1}: {(end_time - start_time):.3f}s - Risk: {component.risk_score:.2f}")
            else:
                print(f"   Run {i+1}: {(end_time - start_time):.3f}s - Failed")
        
        avg_time = sum(times) / len(times)
        performance_data.append({
            'component': part_number,
            'avg_time': avg_time,
            'min_time': min(times),
            'max_time': max(times)
        })
    
    # Show performance summary
    print(f"\n📊 Performance Summary:")
    for data in performance_data:
        print(f"   {data['component']}: Avg={data['avg_time']:.3f}s, "
              f"Min={data['min_time']:.3f}s, Max={data['max_time']:.3f}s")

def demo_error_handling():
    """Demo error handling capabilities"""
    print("\n🛡️ Demo: Error Handling")
    print("=" * 40)
    
    agent = ElectronicComponentAgent()
    
    # Test various error scenarios
    test_cases = [
        ("INVALID123", "Invalid part number"),
        ("TEST456", "Non-existent component"),
        ("", "Empty part number"),
        ("LM741", "Valid component (should work)")
    ]
    
    for part_number, description in test_cases:
        print(f"\n🔍 Testing: {description}")
        print(f"   Part Number: '{part_number}'")
        
        try:
            start_time = time.time()
            result = agent.source_component(part_number)
            end_time = time.time()
            
            if result:
                print(f"   ✅ Success: {result.manufacturer}, Risk: {result.risk_score:.2f}")
            else:
                print(f"   ❌ Failed: Component not found")
            
            print(f"   ⏱️ Response Time: {(end_time - start_time):.3f}s")
            
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")

def main():
    """Run all demos"""
    print("🚀 Electronic Component Agent Demo")
    print("=" * 50)
    
    # Run all demos
    demo_single_component()
    demo_risk_assessment()
    demo_sourcing_optimization()
    demo_performance_comparison()
    demo_error_handling()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("📊 Run 'python test_agent.py' for comprehensive testing")
    print("📈 Check 'agent_test_results.png' for visualizations")

if __name__ == "__main__":
    main() 