import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional


class RailwayAnalyzer:
    """AI-based condition analyzer for railway track fittings"""
    
    def __init__(self, api_base_url: str = "http://localhost:3000"):
        self.api_base_url = api_base_url.rstrip('/')
    
    def fetch_product_data(self, product_id: str) -> Optional[Dict]:
        """Fetch product data from backend API"""
        try:
            response = requests.get(f"{self.api_base_url}/api/products/{product_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for Product ID {product_id}: {e}")
            return None
    
    def calculate_age_months(self, supply_date: str) -> int:
        """Calculate component age in months"""
        supply = datetime.strptime(supply_date, "%Y-%m-%d")
        return (datetime.now() - supply).days // 30
    
    def get_last_inspection_days(self, inspection_dates: list) -> int:
        """Get days since last inspection"""
        if not inspection_dates:
            return float('inf')
        
        latest = max(datetime.strptime(date, "%Y-%m-%d") for date in inspection_dates)
        return (datetime.now() - latest).days
    
    def analyze_condition(self, product_data: Dict) -> Dict:
        """AI-based condition analysis"""
        age_months = self.calculate_age_months(product_data['dateOfSupply'])
        days_since_inspection = self.get_last_inspection_days(product_data['inspectionDates'])
        
        # AI Risk Assessment Logic
        risk_score = 0
        risk_factors = []
        
        # Age-based risk
        if age_months > 48:
            risk_score += 40
            risk_factors.append("Component exceeding recommended service life")
        elif age_months > 36:
            risk_score += 25
            risk_factors.append("Component approaching end of service life")
        elif age_months > 24:
            risk_score += 10
            risk_factors.append("Component in mid-service period")
        
        # Inspection-based risk
        if days_since_inspection > 180:
            risk_score += 35
            risk_factors.append("Overdue for inspection (>6 months)")
        elif days_since_inspection > 90:
            risk_score += 20
            risk_factors.append("Due for inspection soon")
        
        # Status-based risk
        if product_data['status'].lower() in ['faulty', 'damaged', 'worn']:
            risk_score += 50
            risk_factors.append("Component status indicates issues")
        
        # Determine condition level
        if risk_score >= 70:
            condition = "CRITICAL"
            color = "🔴"
        elif risk_score >= 40:
            condition = "WARNING"
            color = "🟡"
        else:
            condition = "GOOD"
            color = "🟢"
        
        return {
            'condition': condition,
            'risk_score': min(risk_score, 100),
            'color': color,
            'risk_factors': risk_factors,
            'age_months': age_months,
            'days_since_inspection': days_since_inspection
        }
    
    def generate_recommendations(self, analysis: Dict, product_data: Dict) -> list:
        """Generate AI-based maintenance recommendations"""
        recommendations = []
        
        if analysis['condition'] == "CRITICAL":
            recommendations.append("🚨 IMMEDIATE ACTION: Replace component immediately")
            recommendations.append("🔧 Schedule emergency maintenance")
            recommendations.append("📋 Conduct thorough safety inspection")
        
        elif analysis['condition'] == "WARNING":
            recommendations.append("⚠️ Schedule replacement within 30 days")
            recommendations.append("🔍 Increase inspection frequency to weekly")
            recommendations.append("📊 Monitor closely for deterioration")
        
        else:
            recommendations.append("✅ Continue normal operation")
            recommendations.append("📅 Maintain regular inspection schedule")
        
        # Inspection-specific recommendations
        if analysis['days_since_inspection'] > 90:
            recommendations.append(f"🔎 Schedule inspection (last: {analysis['days_since_inspection']} days ago)")
        
        # Age-specific recommendations
        if analysis['age_months'] > 36:
            recommendations.append("📈 Consider proactive replacement planning")
        
        return recommendations
    
    def analyze_product(self, product_id: str) -> Dict:
        """Complete analysis workflow for a product"""
        # Fetch product data
        product_data = self.fetch_product_data(product_id)
        if not product_data:
            return {'error': 'Product not found or API error'}
        
        # Perform AI analysis
        analysis = self.analyze_condition(product_data)
        recommendations = self.generate_recommendations(analysis, product_data)
        
        # Compile summary report
        return {
            'product_info': {
                'Product ID': product_data['productId'],
                'Vendor': product_data['vendor'],
                'Batch No': product_data['batchNo'],
                'Supply Date': product_data['dateOfSupply'],
                'Warranty': product_data['warrantyPeriod'],
                'Status': product_data['status']
            },
            'ai_analysis': {
                'Condition': f"{analysis['color']} {analysis['condition']}",
                'Risk Score': f"{analysis['risk_score']}/100",
                'Age': f"{analysis['age_months']} months",
                'Last Inspection': f"{analysis['days_since_inspection']} days ago",
                'Risk Factors': analysis['risk_factors']
            },
            'recommendations': recommendations
        }
    
    def print_report(self, product_id: str):
        """Print formatted analysis report"""
        result = self.analyze_product(product_id)
        
        if 'error' in result:
            print(f"❌ {result['error']}")
            return
        
        print("\n" + "="*60)
        print("🚂 RAILWAY TRACK FITTING AI ANALYSIS REPORT")
        print("="*60)
        
        print("\n📦 PRODUCT INFORMATION:")
        for key, value in result['product_info'].items():
            print(f"  {key}: {value}")
        
        print("\n🤖 AI CONDITION ANALYSIS:")
        for key, value in result['ai_analysis'].items():
            if key == 'Risk Factors':
                print(f"  {key}:")
                for factor in value:
                    print(f"    • {factor}")
            else:
                print(f"  {key}: {value}")
        
        print("\n💡 AI RECOMMENDATIONS:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60)


# Production-ready usage
def main():
    """Main function for production use"""
    analyzer = RailwayAnalyzer("http://localhost:3000")  # Replace with your API URL
    
    # Interactive mode
    while True:
        try:
            product_id = input("\n🔍 Enter Product ID (or 'quit' to exit): ").strip()
            
            if product_id.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not product_id:
                print("❌ Please enter a valid Product ID")
                continue
            
            analyzer.print_report(product_id)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Example usage
    analyzer = RailwayAnalyzer("http://localhost:3000")
    
    # Single product analysis
    result = analyzer.analyze_product("1234")
    print(json.dumps(result, indent=2))
    
    # Interactive mode
    main()