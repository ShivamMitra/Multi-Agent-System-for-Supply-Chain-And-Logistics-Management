
class DemandForecastAgent:
    def __init__(self, context=None):
        self.groq_client = _make_groq_client()
        self.context = context if context is not None else {}

    def generate_demand_forecast(self, historical_sales: list, market_trends: dict, seasonality: dict, economic_data: dict, customer_profiles: list, inventory: dict, competition: dict, feedback: list) -> str:
        """
        Forecast market and customer demand, provide recommendations, and suggest pricing using Groq API (llama-3.3-70b-versatile).
        Args:
            historical_sales (list): List of sales records (dicts)
            market_trends (dict): Market trend data
            seasonality (dict): Seasonality data
            economic_data (dict): Economic indicators
            customer_profiles (list): List of customer profile dicts
            inventory (dict): {product: stock_level}
            competition (dict): {product: competitor_price}
            feedback (list): List of customer feedback strings
        Returns:
            str: Demand forecast report and suggested actions as a string
        """
        prompt = f"""
You are an expert AI agent for demand forecasting and marketing in the electronics supply chain.
Given the following:
- Historical sales: {json.dumps(historical_sales)}
- Market trends: {json.dumps(market_trends)}
- Seasonality: {json.dumps(seasonality)}
- Economic data: {json.dumps(economic_data)}
- Customer profiles: {json.dumps(customer_profiles)}
- Inventory: {json.dumps(inventory)}
- Competition: {json.dumps(competition)}
- Customer feedback: {json.dumps(feedback)}

Your tasks:
- Predict demand at product-category and region levels
- Provide personalized product recommendations
- Suggest dynamic pricing strategies
- Summarize customer feedback for product improvement

Use the Groq API (llama-3.3-70b-versatile) to generate actionable demand forecasts and marketing insights.
Return ONLY the demand forecast report and suggested actions as a string. Do not return any explanation or JSON.
"""
        if not self.groq_client or self.context.get('offline'):
            return self._offline_forecast()
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            report = response.choices[0].message.content.strip()
            return report
        except Exception as e:
            logger.warning(f"Forecast API failed, using offline fallback: {e}")
            return self._offline_forecast()
    
    def _offline_forecast(self) -> str:
        return (
            "Demand forecast: LM741 120 in Europe, LM358 150 in North America, OP07 90 in Asia. "
            "Recommendations: increase LM358 production, maintain LM741, monitor OP07. Pricing: competitive for LM358."
        )
class LogisticsManagerAgent:
    def __init__(self, context=None):
        self.groq_client = _make_groq_client()
        self.context = context if context is not None else {}

    def generate_logistics_plan(self, finished_goods: list, locations: dict, timelines: dict) -> str:
        """
        Manage global logistics and fulfillment for electronic components using Groq API (llama-3.3-70b-versatile).
        Args:
            finished_goods (list): List of dicts with keys: part_number, quantity, destination
            locations (dict): {destination: address or region}
            timelines (dict): {part_number: delivery_deadline}
        Returns:
            str: Optimized shipment plan and warehouse allocation as a string
        """
        prompt = f"""
You are an expert AI agent for global logistics and fulfillment in the electronics supply chain.
Given the following:
- Finished goods: {json.dumps(finished_goods)}
- Locations: {json.dumps(locations)}
- Timelines: {json.dumps(timelines)}

Your tasks:
- Optimize transportation routes and modes (air/sea/road) for each shipment based on cost and speed
- Track shipments in real time and handle warehousing instructions
- Ensure documentation (customs clearance, compliance certificates) is generated
- Plan last-mile delivery and send updates to stakeholders

Use the Groq API (llama-3.3-70b-versatile) to generate logistics decisions and route summaries.
Return ONLY the optimized shipment plan and warehouse allocation as a string. Do not return any explanation or JSON.
"""
        if not self.groq_client or self.context.get('offline'):
            return self._offline_logistics()
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            plan = response.choices[0].message.content.strip()
            return plan
        except Exception as e:
            logger.warning(f"Logistics API failed, using offline fallback: {e}")
            return self._offline_logistics()
    
    def _offline_logistics(self) -> str:
        return (
            "Logistics: consolidate EU shipments to Berlin by road, NA by air to NYC, AS by sea to Tokyo; docs prepared."
        )
    
    def _offline_plan(self) -> str:
        return (
            "Production plan: Produce LM358 600, LM741 300, OP07 100. Reorder OP07 (500), LM358 (300)."
        )
import os
import json
import logging
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import groq
from dotenv import load_dotenv
import pandas as pd
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _make_groq_client():
    """Create Groq client safely. Returns None if construction fails (e.g., proxy/httpx mismatch)."""
    try:
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return None
        return groq.Groq(api_key=api_key)
    except Exception as e:
        logger.warning(f"Groq client initialization failed, falling back to offline mode: {e}")
        return None

@dataclass
class Component:
    part_number: str
    manufacturer: str
    description: str
    stock: int
    price: float
    lead_time: int
    risk_score: float
    alternatives: List[str]

@dataclass
class RiskAssessment:
    component_id: str
    risk_factors: List[str]
    risk_score: float
    mitigation_strategies: List[str]
    supplier_rating: float

class ElectronicComponentAgent:
    def __init__(self, context=None):
        self.groq_client = _make_groq_client()
        self.components_db = {}
        self.risk_assessments = {}
        self.context = context if context is not None else {}
        
    def source_component(self, part_number: str, quantity: int = 1) -> Optional[Component]:
        """Source electronic component with risk assessment"""
        try:
            # Simulate component search
            component_data = self._search_component(part_number)
            if not component_data:
                return None
                
            # Assess risks
            risk_assessment = self._assess_risks(part_number, component_data)
            
            # Create component object
            component = Component(
                part_number=part_number,
                manufacturer=component_data.get('manufacturer', 'Unknown'),
                description=component_data.get('description', ''),
                stock=component_data.get('stock', 0),
                price=component_data.get('price', 0.0),
                lead_time=component_data.get('lead_time', 0),
                risk_score=risk_assessment.risk_score,
                alternatives=component_data.get('alternatives', [])
            )
            
            self.components_db[part_number] = component
            self.risk_assessments[part_number] = risk_assessment
            
            return component
            
        except Exception as e:
            logger.error(f"Error sourcing component {part_number}: {e}")
            return None
    
    def _search_component(self, part_number: str) -> Dict:
        """Search for component data (simulated)"""
        # Simulate API call to component database
        mock_data = {
            'manufacturer': 'Texas Instruments',
            'description': 'High-speed operational amplifier',
            'stock': 1500,
            'price': 2.45,
            'lead_time': 14,
            'alternatives': ['LM358', 'OP07', 'AD822']
        }
        return mock_data
    
    def _assess_risks(self, part_number: str, component_data: Dict) -> RiskAssessment:
        """Assess component risks using Groq API"""
        try:
            prompt = f"""
            You are a risk assessment expert for electronic components. Analyze the following component:

            Component: {part_number}
            Manufacturer: {component_data.get('manufacturer')}
            Stock: {component_data.get('stock')}
            Lead time: {component_data.get('lead_time')} days
            Price: ${component_data.get('price')}

            Return ONLY a valid JSON object with this exact structure:
            {{
                "risk_factors": ["risk1", "risk2"],
                "risk_score": 5.0,
                "mitigation_strategies": ["strategy1", "strategy2"],
                "supplier_rating": 7.0
            }}

            Risk factors should consider: supply chain disruption, obsolescence, price volatility, quality issues.
            Risk score: 0-10 (0=low risk, 10=high risk)
            Supplier rating: 0-10 (0=poor, 10=excellent)
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"Raw response: {content}")
            
            # Try to extract JSON from response
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    # Fallback to default values
                    result = {
                        'risk_factors': ['Supply chain risk', 'Price volatility'],
                        'risk_score': 5.0,
                        'mitigation_strategies': ['Diversify suppliers', 'Monitor prices'],
                        'supplier_rating': 6.0
                    }
            
            return RiskAssessment(
                component_id=part_number,
                risk_factors=result.get('risk_factors', []),
                risk_score=float(result.get('risk_score', 5.0)),
                mitigation_strategies=result.get('mitigation_strategies', []),
                supplier_rating=float(result.get('supplier_rating', 5.0))
            )
            
        except Exception as e:
            logger.error(f"Error assessing risks: {e}")
            return RiskAssessment(
                component_id=part_number,
                risk_factors=['Supply chain risk', 'Price volatility'],
                risk_score=5.0,
                mitigation_strategies=['Diversify suppliers', 'Monitor prices'],
                supplier_rating=6.0
            )
    
    def get_risk_report(self, part_number: str) -> Optional[Dict]:
        """Generate risk report for component"""
        if part_number not in self.risk_assessments:
            return None
            
        assessment = self.risk_assessments[part_number]
        component = self.components_db.get(part_number)
        
        return {
            'part_number': part_number,
            'risk_score': assessment.risk_score,
            'risk_factors': assessment.risk_factors,
            'mitigation_strategies': assessment.mitigation_strategies,
            'supplier_rating': assessment.supplier_rating,
            'component_info': {
                'manufacturer': component.manufacturer if component else 'Unknown',
                'stock': component.stock if component else 0,
                'price': component.price if component else 0.0,
                'lead_time': component.lead_time if component else 0
            } if component else {}
        }
    
    def optimize_sourcing(self, components: List[str]) -> Dict:
        """Optimize sourcing strategy for multiple components"""
        try:
            if not self.groq_client:
                return {
                    'recommended_suppliers': ['Digi-Key', 'Mouser', 'Arrow'],
                    'cost_optimization': ['Bulk purchasing', 'Volume discounts'],
                    'risk_mitigation': ['Multiple suppliers', 'Safety stock'],
                    'timeline': '4-6 weeks'
                }
            prompt = f"""
            You are a sourcing optimization expert. Optimize sourcing for these components: {components}

            Return ONLY a valid JSON object with this exact structure:
            {{
                "recommended_suppliers": ["supplier1", "supplier2"],
                "cost_optimization": ["strategy1", "strategy2"],
                "risk_mitigation": ["strategy1", "strategy2"],
                "timeline": "estimated timeline"
            }}

            Consider: bulk purchasing, supplier diversification, lead time optimization, quality assurance.
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"Optimization raw response: {content}")
            
            # Try to extract JSON from response
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    # Fallback to default values
                    result = {
                        'recommended_suppliers': ['Digi-Key', 'Mouser', 'Arrow'],
                        'cost_optimization': ['Bulk purchasing', 'Volume discounts'],
                        'risk_mitigation': ['Multiple suppliers', 'Safety stock'],
                        'timeline': '4-6 weeks'
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing sourcing: {e}")
            return {
                'recommended_suppliers': ['Digi-Key', 'Mouser', 'Arrow'],
                'cost_optimization': ['Bulk purchasing', 'Volume discounts'],
                'risk_mitigation': ['Multiple suppliers', 'Safety stock'],
                'timeline': '4-6 weeks'
            }

class ComponentSourcingAgent:
    def __init__(self, context=None):
        self.groq_client = _make_groq_client()
        self.context = context if context is not None else {}
        self.component_agent = ElectronicComponentAgent(context=self.context)

    def extract_requirements_from_forecast(self, forecast_report: str) -> List[Dict]:
        """Extract component requirements (part_number and quantity) from a natural language forecast report."""
        try:
            if not self.groq_client:
                # Heuristic extraction in offline mode (very simple keyword-based fallback)
                requirements: List[Dict] = []
                for token in ["LM741", "LM358", "OP07"]:
                    if token in (forecast_report or ""):
                        qty = 100 if token == "LM741" else 80 if token == "LM358" else 60
                        requirements.append({"part_number": token, "quantity": qty})
                return requirements
            prompt = f"""
You are an expert assistant. Read the following demand forecast report and extract a concise list of component requirements.

Report:
{forecast_report}

Return ONLY valid JSON with this exact structure:
{{
  "requirements": [
    {{"part_number": "LM741", "quantity": 100}},
    {{"part_number": "LM358", "quantity": 80}}
  ]
}}
"""
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            content = response.choices[0].message.content.strip()
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                parsed = json.loads(json_match.group()) if json_match else {"requirements": []}
            requirements = parsed.get("requirements", [])
            # Basic validation/coercion
            normalized = []
            for item in requirements:
                pn = str(item.get("part_number", "")).strip()
                qty = int(item.get("quantity", 0)) if str(item.get("quantity", "0")).isdigit() else 0
                if pn and qty > 0:
                    normalized.append({"part_number": pn, "quantity": qty})
            return normalized
        except Exception as e:
            logger.error(f"Error extracting requirements: {e}")
            return []

    def source_requirements(self, requirements: List[Dict]) -> Dict[str, Dict]:
        """Source a list of component requirements and attach risk reports."""
        results: Dict[str, Dict] = {}
        for req in requirements:
            part_number = req.get("part_number")
            quantity = int(req.get("quantity", 0))
            if not part_number or quantity <= 0:
                continue
            component = self.component_agent.source_component(part_number, quantity=quantity)
            risk = self.component_agent.get_risk_report(part_number)
            results[part_number] = {
                "requested_quantity": quantity,
                "component": component.__dict__ if component else None,
                "risk_report": risk
            }
        # Save into shared context
        self.context["sourcing_results"] = results
        return results

def main():
    """Main function to demonstrate the agent"""
    agent = ElectronicComponentAgent()
    
    # Example usage
    component = agent.source_component("LM741", quantity=100)
    if component:
        print(f"Component sourced: {component.part_number}")
        print(f"Risk score: {component.risk_score}")
        
        risk_report = agent.get_risk_report("LM741")
        print(f"Risk report: {json.dumps(risk_report, indent=2)}")
        
        optimization = agent.optimize_sourcing(["LM741", "LM358", "OP07"])
        print(f"Optimization: {json.dumps(optimization, indent=2)}")


# --- New Agent for Production Scheduling and Inventory Optimization ---
class ProductionSchedulerAgent:
    def __init__(self, context=None):
        self.groq_client = _make_groq_client()
        self.context = context if context is not None else {}

    def generate_production_plan(self, components: list, stock_levels: dict, production_capacity: int) -> str:
        """
        Generate an optimal production schedule and reorder recommendations using Groq API (llama-3.3-70b-versatile).
        Args:
            components (list): List of dicts with keys: part_number, lead_time, available_qty
            stock_levels (dict): {part_number: current_stock}
            production_capacity (int): Max units that can be produced per cycle
        Returns:
            str: Final production plan as a string
        """
        prompt = f"""
You are an expert AI agent for electronics supply chain production scheduling and inventory optimization.
Given the following:
- Components (with part numbers, available quantities, and lead times): {json.dumps(components)}
- Current stock levels: {json.dumps(stock_levels)}
- Production capacity: {production_capacity} units per cycle

Analyze the data and output ONLY the final production plan as a string. The plan should include:
- Optimal production schedule (what to produce, when, and how much)
- Reorder recommendations (which components to reorder, how many, and when)
Do not return any explanation or JSON, only the final production plan as a string.
"""
        if not self.groq_client or self.context.get('offline'):
            return self._offline_plan()
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            plan = response.choices[0].message.content.strip()
            return plan
        except Exception as e:
            logger.warning(f"Production API failed, using offline fallback: {e}")
            return self._offline_plan()

    def _offline_plan(self) -> str:
        # Include explicit product quantities to support UI parsing
        return "Production plan: Produce LM358 600, LM741 300, OP07 100. Reorder OP07 (500), LM358 (300)."

if __name__ == "__main__":
    main()
