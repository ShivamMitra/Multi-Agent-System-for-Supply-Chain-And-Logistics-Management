import json
import time
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
from typing import List, Dict
import numpy as np
from agent import ElectronicComponentAgent, Component, RiskAssessment

class AgentTester:
    def __init__(self):
        self.agent = ElectronicComponentAgent()
        self.test_results = []
        self.performance_metrics = {}
        
    def run_comprehensive_test(self):
        """Run comprehensive testing of the agent"""
        print("🚀 Starting Comprehensive Agent Testing")
        print("=" * 50)
        
        # Test 1: Single Component Sourcing
        self.test_single_component_sourcing()
        
        # Test 2: Multiple Component Sourcing
        self.test_multiple_component_sourcing()
        
        # Test 3: Risk Assessment Analysis
        self.test_risk_assessment()
        
        # Test 4: Sourcing Optimization
        self.test_sourcing_optimization()
        
        # Test 5: Performance Testing
        self.test_performance()
        
        # Test 6: Error Handling
        self.test_error_handling()
        
        # Generate Visualizations
        self.generate_visualizations()
        
        # Print Summary
        self.print_test_summary()
    
    def test_single_component_sourcing(self):
        """Test single component sourcing functionality"""
        print("\n📦 Test 1: Single Component Sourcing")
        print("-" * 30)
        
        test_components = [
            "LM741", "LM358", "OP07", "AD822", "TL072",
            "NE555", "LM324", "LM386", "LM7805", "LM317"
        ]
        
        for component in test_components:
            start_time = time.time()
            result = self.agent.source_component(component, quantity=100)
            end_time = time.time()
            
            if result:
                self.test_results.append({
                    'test_type': 'single_sourcing',
                    'component': component,
                    'success': True,
                    'risk_score': result.risk_score,
                    'price': result.price,
                    'lead_time': result.lead_time,
                    'response_time': end_time - start_time,
                    'timestamp': datetime.now()
                })
                print(f"✅ {component}: Risk={result.risk_score:.2f}, Price=${result.price:.2f}, Lead={result.lead_time} days")
            else:
                self.test_results.append({
                    'test_type': 'single_sourcing',
                    'component': component,
                    'success': False,
                    'response_time': end_time - start_time,
                    'timestamp': datetime.now()
                })
                print(f"❌ {component}: Failed to source")
    
    def test_multiple_component_sourcing(self):
        """Test sourcing multiple components simultaneously"""
        print("\n🔗 Test 2: Multiple Component Sourcing")
        print("-" * 30)
        
        component_batches = [
            ["LM741", "LM358", "OP07"],
            ["NE555", "LM324", "LM386"],
            ["LM7805", "LM317", "LM1117"]
        ]
        
        for i, batch in enumerate(component_batches, 1):
            start_time = time.time()
            results = []
            
            for component in batch:
                result = self.agent.source_component(component, quantity=50)
                if result:
                    results.append(result)
            
            end_time = time.time()
            
            avg_risk = np.mean([r.risk_score for r in results]) if results else 0
            avg_price = np.mean([r.price for r in results]) if results else 0
            
            self.test_results.append({
                'test_type': 'batch_sourcing',
                'batch_id': i,
                'components': batch,
                'success_count': len(results),
                'total_components': len(batch),
                'avg_risk_score': avg_risk,
                'avg_price': avg_price,
                'response_time': end_time - start_time,
                'timestamp': datetime.now()
            })
            
            print(f"📦 Batch {i}: {len(results)}/{len(batch)} successful, Avg Risk={avg_risk:.2f}")
    
    def test_risk_assessment(self):
        """Test risk assessment functionality"""
        print("\n⚠️ Test 3: Risk Assessment Analysis")
        print("-" * 30)
        
        # Test components with different risk profiles
        risk_test_components = ["LM741", "LM358", "OP07", "AD822", "TL072"]
        
        for component in risk_test_components:
            # Source component first
            comp = self.agent.source_component(component)
            if comp:
                # Get detailed risk report
                risk_report = self.agent.get_risk_report(component)
                
                if risk_report:
                    self.test_results.append({
                        'test_type': 'risk_assessment',
                        'component': component,
                        'risk_score': risk_report['risk_score'],
                        'risk_factors_count': len(risk_report['risk_factors']),
                        'mitigation_strategies_count': len(risk_report['mitigation_strategies']),
                        'supplier_rating': risk_report['supplier_rating'],
                        'timestamp': datetime.now()
                    })
                    
                    print(f"🔍 {component}: Risk={risk_report['risk_score']:.2f}, "
                          f"Factors={len(risk_report['risk_factors'])}, "
                          f"Supplier Rating={risk_report['supplier_rating']:.2f}")
    
    def test_sourcing_optimization(self):
        """Test sourcing optimization functionality"""
        print("\n🎯 Test 4: Sourcing Optimization")
        print("-" * 30)
        
        optimization_scenarios = [
            ["LM741", "LM358", "OP07"],
            ["NE555", "LM324", "LM386", "LM7805"],
            ["AD822", "TL072", "LM1117", "LM317", "LM386"]
        ]
        
        for i, scenario in enumerate(optimization_scenarios, 1):
            start_time = time.time()
            optimization = self.agent.optimize_sourcing(scenario)
            end_time = time.time()
            
            if 'error' not in optimization:
                self.test_results.append({
                    'test_type': 'optimization',
                    'scenario_id': i,
                    'components_count': len(scenario),
                    'suppliers_count': len(optimization.get('recommended_suppliers', [])),
                    'strategies_count': len(optimization.get('cost_optimization', [])),
                    'response_time': end_time - start_time,
                    'timestamp': datetime.now()
                })
                
                print(f"🎯 Scenario {i}: {len(scenario)} components, "
                      f"{len(optimization.get('recommended_suppliers', []))} suppliers, "
                      f"{len(optimization.get('cost_optimization', []))} strategies")
            else:
                print(f"❌ Scenario {i}: Optimization failed")
    
    def test_performance(self):
        """Test agent performance under different loads"""
        print("\n⚡ Test 5: Performance Testing")
        print("-" * 30)
        
        # Test response times for different component types
        performance_components = ["LM741", "LM358", "OP07", "NE555", "LM324"]
        
        response_times = []
        for component in performance_components:
            times = []
            for _ in range(3):  # Test each component 3 times
                start_time = time.time()
                self.agent.source_component(component)
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = np.mean(times)
            response_times.append(avg_time)
            
            self.test_results.append({
                'test_type': 'performance',
                'component': component,
                'avg_response_time': avg_time,
                'min_response_time': min(times),
                'max_response_time': max(times),
                'timestamp': datetime.now()
            })
            
            print(f"⚡ {component}: Avg={avg_time:.3f}s, Min={min(times):.3f}s, Max={max(times):.3f}s")
        
        self.performance_metrics['avg_response_time'] = np.mean(response_times)
        self.performance_metrics['max_response_time'] = max(response_times)
    
    def test_error_handling(self):
        """Test error handling capabilities"""
        print("\n🛡️ Test 6: Error Handling")
        print("-" * 30)
        
        # Test with invalid components
        invalid_components = ["INVALID123", "TEST456", "FAKE789"]
        
        for component in invalid_components:
            start_time = time.time()
            result = self.agent.source_component(component)
            end_time = time.time()
            
            self.test_results.append({
                'test_type': 'error_handling',
                'component': component,
                'success': result is not None,
                'response_time': end_time - start_time,
                'timestamp': datetime.now()
            })
            
            if result:
                print(f"⚠️ {component}: Unexpected success")
            else:
                print(f"✅ {component}: Properly handled as invalid")
    
    def generate_visualizations(self):
        """Generate comprehensive visualizations"""
        print("\n📊 Generating Visualizations...")
        
        # Convert test results to DataFrame
        df = pd.DataFrame(self.test_results)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Electronic Component Agent - Comprehensive Test Results', fontsize=16, fontweight='bold')
        
        # 1. Risk Score Distribution
        if not df.empty and 'risk_score' in df.columns:
            risk_data = df[df['risk_score'].notna()]
            if not risk_data.empty:
                axes[0, 0].hist(risk_data['risk_score'], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
                axes[0, 0].set_title('Risk Score Distribution')
                axes[0, 0].set_xlabel('Risk Score')
                axes[0, 0].set_ylabel('Frequency')
                axes[0, 0].axvline(risk_data['risk_score'].mean(), color='red', linestyle='--', label=f'Mean: {risk_data["risk_score"].mean():.2f}')
                axes[0, 0].legend()
        
        # 2. Response Time Analysis
        if not df.empty and 'response_time' in df.columns:
            response_data = df[df['response_time'].notna()]
            if not response_data.empty:
                axes[0, 1].boxplot(response_data['response_time'])
                axes[0, 1].set_title('Response Time Distribution')
                axes[0, 1].set_ylabel('Time (seconds)')
                axes[0, 1].set_xticklabels(['All Tests'])
        
        # 3. Success Rate by Test Type
        if not df.empty and 'test_type' in df.columns:
            success_rates = df.groupby('test_type')['success'].mean()
            axes[0, 2].bar(success_rates.index, success_rates.values, color='lightgreen', alpha=0.7)
            axes[0, 2].set_title('Success Rate by Test Type')
            axes[0, 2].set_ylabel('Success Rate')
            axes[0, 2].tick_params(axis='x', rotation=45)
        
        # 4. Component Price vs Risk Score
        if not df.empty and 'price' in df.columns and 'risk_score' in df.columns:
            price_risk_data = df[df['price'].notna() & df['risk_score'].notna()]
            if not price_risk_data.empty:
                axes[1, 0].scatter(price_risk_data['price'], price_risk_data['risk_score'], alpha=0.6)
                axes[1, 0].set_title('Price vs Risk Score')
                axes[1, 0].set_xlabel('Price ($)')
                axes[1, 0].set_ylabel('Risk Score')
        
        # 5. Lead Time Analysis
        if not df.empty and 'lead_time' in df.columns:
            lead_time_data = df[df['lead_time'].notna()]
            if not lead_time_data.empty:
                axes[1, 1].hist(lead_time_data['lead_time'], bins=8, alpha=0.7, color='orange', edgecolor='black')
                axes[1, 1].set_title('Lead Time Distribution')
                axes[1, 1].set_xlabel('Lead Time (days)')
                axes[1, 1].set_ylabel('Frequency')
        
        # 6. Test Performance Timeline
        if not df.empty and 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            test_counts = df.groupby(df['timestamp'].dt.hour).size()
            axes[1, 2].plot(test_counts.index, test_counts.values, marker='o', linewidth=2, markersize=8)
            axes[1, 2].set_title('Test Execution Timeline')
            axes[1, 2].set_xlabel('Hour of Day')
            axes[1, 2].set_ylabel('Number of Tests')
        
        plt.tight_layout()
        plt.savefig('agent_test_results.png', dpi=300, bbox_inches='tight')
        print("📈 Visualizations saved as 'agent_test_results.png'")
        
        # Generate detailed statistics
        self.generate_statistics_report(df)
    
    def generate_statistics_report(self, df):
        """Generate detailed statistics report"""
        print("\n📋 Detailed Statistics Report")
        print("=" * 40)
        
        if df.empty:
            print("No test data available")
            return
        
        # Overall statistics
        total_tests = len(df)
        successful_tests = len(df[df['success'] == True]) if 'success' in df.columns else 0
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful Tests: {successful_tests}")
        print(f"Success Rate: {success_rate:.2f}%")
        
        # Risk assessment statistics
        if 'risk_score' in df.columns:
            risk_data = df[df['risk_score'].notna()]
            if not risk_data.empty:
                print(f"\nRisk Assessment Statistics:")
                print(f"Average Risk Score: {risk_data['risk_score'].mean():.2f}")
                print(f"Risk Score Std Dev: {risk_data['risk_score'].std():.2f}")
                print(f"Min Risk Score: {risk_data['risk_score'].min():.2f}")
                print(f"Max Risk Score: {risk_data['risk_score'].max():.2f}")
        
        # Performance statistics
        if 'response_time' in df.columns:
            response_data = df[df['response_time'].notna()]
            if not response_data.empty:
                print(f"\nPerformance Statistics:")
                print(f"Average Response Time: {response_data['response_time'].mean():.3f}s")
                print(f"Max Response Time: {response_data['response_time'].max():.3f}s")
                print(f"Min Response Time: {response_data['response_time'].min():.3f}s")
        
        # Test type breakdown
        if 'test_type' in df.columns:
            print(f"\nTest Type Breakdown:")
            test_counts = df['test_type'].value_counts()
            for test_type, count in test_counts.items():
                print(f"  {test_type}: {count} tests")
    
    def print_test_summary(self):
        """Print final test summary"""
        print("\n" + "=" * 50)
        print("🎯 FINAL TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.get('success', True)])
        
        print(f"Total Tests Executed: {total_tests}")
        print(f"Successful Tests: {successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        if self.performance_metrics:
            print(f"Average Response Time: {self.performance_metrics.get('avg_response_time', 0):.3f}s")
            print(f"Maximum Response Time: {self.performance_metrics.get('max_response_time', 0):.3f}s")
        
        print("\n✅ Testing completed successfully!")
        print("📊 Check 'agent_test_results.png' for visualizations")

def main():
    """Main function to run comprehensive testing"""
    tester = AgentTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 