"""
Data Analytics Engine for Travelopedia
Provides historical data analysis, trend detection, and insights
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from collections import defaultdict


class TravelDataAnalytics:
    """Analytics engine for travel data insights."""
    
    def __init__(self, data_dir="output"):
        """Initialize analytics engine."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / "trip_history.json"
        self.analytics_cache = {}
    
    def load_history(self):
        """Load trip history from file."""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_trip(self, trip_data):
        """Save trip to history."""
        history = self.load_history()
        
        trip_record = {
            'id': len(history) + 1,
            'timestamp': datetime.now().isoformat(),
            'destination': trip_data.get('destination'),
            'origin': trip_data.get('origin'),
            'dates': trip_data.get('dates'),
            'total_cost': trip_data.get('total_cost', 0),
            'budget': trip_data.get('budget', 0),
            'carbon_footprint': trip_data.get('carbon_footprint', 0),
            'preferences': trip_data.get('preferences', []),
            'rating': trip_data.get('rating', 0)
        }
        
        history.append(trip_record)
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return trip_record
    
    def get_destination_stats(self, destination):
        """Get statistics for a specific destination."""
        history = self.load_history()
        
        dest_trips = [t for t in history if t.get('destination') == destination]
        
        if not dest_trips:
            return None
        
        costs = [t['total_cost'] for t in dest_trips if 'total_cost' in t]
        carbon = [t['carbon_footprint'] for t in dest_trips if 'carbon_footprint' in t]
        
        return {
            'trip_count': len(dest_trips),
            'avg_cost': np.mean(costs) if costs else 0,
            'min_cost': np.min(costs) if costs else 0,
            'max_cost': np.max(costs) if costs else 0,
            'avg_carbon': np.mean(carbon) if carbon else 0,
            'last_visited': dest_trips[-1].get('timestamp') if dest_trips else None
        }
    
    def get_price_trends(self, destination, days=30):
        """Generate price trend data for a destination."""
        # In a real implementation, this would query historical pricing data
        # For now, we'll generate realistic sample data
        
        base_price = np.random.randint(800, 1500)
        dates = [(datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d') 
                 for i in range(days)]
        
        # Simulate seasonal trends
        trend = np.sin(np.linspace(0, 2*np.pi, days)) * 100
        noise = np.random.normal(0, 50, days)
        prices = base_price + trend + noise
        
        return {
            'dates': dates,
            'prices': prices.tolist(),
            'average': float(np.mean(prices)),
            'trend': 'increasing' if prices[-1] > prices[0] else 'decreasing'
        }
    
    def get_popular_destinations(self, limit=10):
        """Get most popular destinations from history."""
        history = self.load_history()
        
        dest_counts = defaultdict(int)
        for trip in history:
            dest = trip.get('destination')
            if dest:
                dest_counts[dest] += 1
        
        sorted_dests = sorted(dest_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'destination': dest, 'count': count}
            for dest, count in sorted_dests[:limit]
        ]
    
    def get_budget_insights(self, budget, destination):
        """Get insights about budget allocation."""
        history = self.load_history()
        
        # Find similar trips
        similar_trips = [
            t for t in history
            if t.get('destination') == destination and
            abs(t.get('budget', 0) - budget) < budget * 0.2
        ]
        
        if not similar_trips:
            return self._get_default_budget_breakdown(budget)
        
        # Calculate average breakdown
        avg_breakdown = {
            'Flights': budget * 0.35,
            'Hotels': budget * 0.30,
            'Activities': budget * 0.15,
            'Food': budget * 0.12,
            'Transport': budget * 0.05,
            'Other': budget * 0.03
        }
        
        return avg_breakdown
    
    def _get_default_budget_breakdown(self, budget):
        """Get default budget breakdown."""
        return {
            'Flights': budget * 0.35,
            'Hotels': budget * 0.30,
            'Activities': budget * 0.15,
            'Food': budget * 0.12,
            'Transport': budget * 0.05,
            'Other': budget * 0.03
        }
    
    def calculate_carbon_footprint(self, flight_distance, hotel_nights, activities_count):
        """Calculate estimated carbon footprint."""
        # Average emissions per km for flights
        flight_carbon = flight_distance * 0.115  # kg CO2 per km
        
        # Average emissions per hotel night
        hotel_carbon = hotel_nights * 20  # kg CO2 per night
        
        # Average emissions for activities
        activity_carbon = activities_count * 5  # kg CO2 per activity
        
        total_carbon = flight_carbon + hotel_carbon + activity_carbon
        
        return {
            'total': round(total_carbon, 2),
            'flight': round(flight_carbon, 2),
            'hotel': round(hotel_carbon, 2),
            'activities': round(activity_carbon, 2),
            'trees_to_offset': int(total_carbon / 20)  # ~20kg CO2 per tree per year
        }
    
    def get_seasonal_insights(self, destination, month):
        """Get seasonal insights for a destination."""
        # Sample seasonal data (in real app, this would come from historical data)
        seasonal_factors = {
            'peak_season': month in [6, 7, 8, 12],  # Summer and December
            'shoulder_season': month in [4, 5, 9, 10],
            'off_season': month in [1, 2, 3, 11]
        }
        
        price_multiplier = 1.0
        if seasonal_factors['peak_season']:
            price_multiplier = 1.3
        elif seasonal_factors['shoulder_season']:
            price_multiplier = 1.1
        else:
            price_multiplier = 0.85
        
        return {
            'season_type': 'peak' if seasonal_factors['peak_season'] else 
                          'shoulder' if seasonal_factors['shoulder_season'] else 'off',
            'price_multiplier': price_multiplier,
            'crowd_level': 'high' if seasonal_factors['peak_season'] else 
                          'moderate' if seasonal_factors['shoulder_season'] else 'low',
            'recommendation': self._get_seasonal_recommendation(seasonal_factors)
        }
    
    def _get_seasonal_recommendation(self, factors):
        """Get recommendation based on season."""
        if factors['peak_season']:
            return "Peak season - Book early for best prices. Expect crowds."
        elif factors['shoulder_season']:
            return "Shoulder season - Great balance of weather and prices."
        else:
            return "Off season - Best prices! Perfect for budget travelers."
    
    def analyze_user_preferences(self, user_history):
        """Analyze user travel preferences from history."""
        if not user_history:
            return {}
        
        # Aggregate preferences
        all_prefs = []
        for trip in user_history:
            prefs = trip.get('preferences', [])
            all_prefs.extend(prefs)
        
        # Count preference frequencies
        pref_counts = defaultdict(int)
        for pref in all_prefs:
            pref_counts[pref] += 1
        
        # Get top preferences
        top_prefs = sorted(pref_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'top_preferences': [p[0] for p in top_prefs],
            'preference_scores': dict(top_prefs),
            'total_trips': len(user_history)
        }
    
    def get_savings_opportunities(self, itinerary_data):
        """Identify potential savings opportunities."""
        opportunities = []
        
        total_cost = itinerary_data.get('total_cost', 0)
        budget = itinerary_data.get('budget', 0)
        
        # Check flight savings
        flight_cost = itinerary_data.get('flight_cost', 0)
        if flight_cost > total_cost * 0.4:
            opportunities.append({
                'category': 'Flights',
                'potential_savings': flight_cost * 0.15,
                'suggestion': 'Consider booking with flexible dates or alternative airports'
            })
        
        # Check hotel savings
        hotel_cost = itinerary_data.get('hotel_cost', 0)
        if hotel_cost > total_cost * 0.35:
            opportunities.append({
                'category': 'Hotels',
                'potential_savings': hotel_cost * 0.20,
                'suggestion': 'Look for hotels slightly outside city center or consider Airbnb'
            })
        
        # Check if over budget
        if total_cost > budget:
            opportunities.append({
                'category': 'Overall',
                'potential_savings': total_cost - budget,
                'suggestion': 'Review alternative itineraries or adjust travel dates'
            })
        
        return opportunities
    
    def generate_comparison_metrics(self, itinerary, alternatives):
        """Generate comparison metrics for itinerary alternatives."""
        all_options = [itinerary] + alternatives
        
        metrics = []
        for idx, option in enumerate(all_options):
            metrics.append({
                'option_id': idx,
                'name': f"Option {idx + 1}" if idx > 0 else "Recommended",
                'total_cost': option.get('total_cost', 0),
                'value_score': option.get('overall_score', 0),
                'carbon_footprint': option.get('carbon_footprint', 0),
                'comfort_level': option.get('comfort_level', 'standard'),
                'activities_count': len(option.get('activities', []))
            })
        
        return metrics
