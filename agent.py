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
    def __init__(self):
        self.groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.components_db = {}
        self.risk_assessments = {}
        
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
                model="llama3-8b-8192",
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
                model="llama3-8b-8192",
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

if __name__ == "__main__":
    main()
