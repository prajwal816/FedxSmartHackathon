"""
Analytics Engine Service
Provides comprehensive analytics and insights for route optimization
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from ..utils.cache_manager import CacheManager
from ..models.analytics_models import DashboardMetrics, RouteComparison

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Advanced analytics for route optimization insights"""
    
    def __init__(self):
        self.cache = CacheManager()
    
    def get_dashboard_metrics(self, time_range: str = '24h') -> Dict:
        """
        Get comprehensive dashboard metrics
        
        Args:
            time_range: Time range for metrics ('1h', '24h', '7d', '30d')
            
        Returns:
            Dashboard metrics and KPIs
        """
        try:
            logger.info(f"Generating dashboard metrics for {time_range}")
            
            # Parse time range
            hours = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get route data from cache/database
            route_data = self._get_route_data(start_time)
            
            if not route_data:
                return self._get_empty_dashboard()
            
            # Calculate key metrics
            metrics = {
                'summary': self._calculate_summary_metrics(route_data),
                'efficiency': self._calculate_efficiency_metrics(route_data),
                'sustainability': self._calculate_sustainability_metrics(route_data),
                'trends': self._calculate_trend_metrics(route_data, hours),
                'performance': self._calculate_performance_metrics(route_data),
                'time_range': time_range,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            logger.info("Dashboard metrics generated successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard metrics: {str(e)}")
            return self._get_empty_dashboard()
    
    def compare_routes(self, route_ids: List[str], metrics: List[str] = None) -> Dict:
        """
        Compare multiple routes across specified metrics
        
        Args:
            route_ids: List of route IDs to compare
            metrics: List of metrics to compare
            
        Returns:
            Detailed route comparison
        """
        try:
            if not metrics:
                metrics = ['time', 'distance', 'fuel', 'emissions']
            
            logger.info(f"Comparing {len(route_ids)} routes on {len(metrics)} metrics")
            
            comparison_data = {}
            route_details = {}
            
            # Get data for each route
            for route_id in route_ids:
                route_data = self.cache.get_route(route_id)
                if route_data:
                    route_details[route_id] = self._extract_route_metrics(route_data, metrics)
            
            if not route_details:
                return {'error': 'No valid routes found for comparison'}
            
            # Calculate comparisons
            comparison_data = {
                'routes': route_details,
                'best_performers': self._find_best_performers(route_details, metrics),
                'statistical_summary': self._calculate_statistical_summary(route_details, metrics),
                'recommendations': self._generate_comparison_recommendations(route_details, metrics),
                'comparison_timestamp': datetime.utcnow().isoformat()
            }
            
            return comparison_data
            
        except Exception as e:
            logger.error(f"Route comparison failed: {str(e)}")
            return {'error': 'Route comparison failed'}
    
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours"""
        time_map = {
            '1h': 1,
            '24h': 24,
            '7d': 168,
            '30d': 720
        }
        return time_map.get(time_range, 24)
    
    def _get_route_data(self, start_time: datetime) -> List[Dict]:
        """Get route data from specified time period"""
        # In a real implementation, this would query a database
        # For demo purposes, we'll generate sample data
        
        sample_routes = []
        for i in range(10):  # Generate 10 sample routes
            route = {
                'route_id': f'route_{i}',
                'timestamp': start_time + timedelta(hours=i),
                'total_distance_km': np.random.uniform(50, 200),
                'total_time_minutes': np.random.uniform(120, 480),
                'fuel_consumed_liters': np.random.uniform(15, 60),
                'total_co2_kg': np.random.uniform(8, 35),
                'stops_count': np.random.randint(5, 25),
                'vehicle_type': np.random.choice(['diesel_truck', 'electric_truck', 'hybrid_truck']),
                'green_score': np.random.randint(40, 95)
            }
            sample_routes.append(route)
        
        return sample_routes
    
    def _get_empty_dashboard(self) -> Dict:
        """Return empty dashboard structure"""
        return {
            'summary': {
                'total_routes': 0,
                'total_distance_km': 0,
                'total_emissions_kg': 0,
                'average_green_score': 0
            },
            'efficiency': {},
            'sustainability': {},
            'trends': {},
            'performance': {},
            'time_range': '24h',
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _calculate_summary_metrics(self, route_data: List[Dict]) -> Dict:
        """Calculate high-level summary metrics"""
        if not route_data:
            return {}
        
        df = pd.DataFrame(route_data)
        
        return {
            'total_routes': len(route_data),
            'total_distance_km': round(df['total_distance_km'].sum(), 2),
            'total_time_hours': round(df['total_time_minutes'].sum() / 60, 2),
            'total_fuel_liters': round(df['fuel_consumed_liters'].sum(), 2),
            'total_emissions_kg': round(df['total_co2_kg'].sum(), 2),
            'total_stops': int(df['stops_count'].sum()),
            'average_green_score': round(df['green_score'].mean(), 1),
            'routes_optimized': len(route_data)
        }
    
    def _calculate_efficiency_metrics(self, route_data: List[Dict]) -> Dict:
        """Calculate efficiency-related metrics"""
        if not route_data:
            return {}
        
        df = pd.DataFrame(route_data)
        
        # Calculate efficiency ratios
        df['km_per_hour'] = df['total_distance_km'] / (df['total_time_minutes'] / 60)
        df['stops_per_hour'] = df['stops_count'] / (df['total_time_minutes'] / 60)
        df['fuel_efficiency'] = df['total_distance_km'] / df['fuel_consumed_liters']
        
        return {
            'average_speed_kmh': round(df['km_per_hour'].mean(), 2),
            'average_stops_per_hour': round(df['stops_per_hour'].mean(), 2),
            'average_fuel_efficiency_km_per_l': round(df['fuel_efficiency'].mean(), 2),
            'time_savings_vs_baseline': self._calculate_time_savings(df),
            'distance_optimization_ratio': self._calculate_distance_optimization(df)
        }
    
    def _calculate_sustainability_metrics(self, route_data: List[Dict]) -> Dict:
        """Calculate sustainability and environmental metrics"""
        if not route_data:
            return {}
        
        df = pd.DataFrame(route_data)
        
        # Vehicle type distribution
        vehicle_distribution = df['vehicle_type'].value_counts().to_dict()
        
        # Calculate emission metrics
        df['co2_per_km'] = df['total_co2_kg'] / df['total_distance_km']
        
        return {
            'average_co2_per_km': round(df['co2_per_km'].mean(), 3),
            'total_co2_saved_vs_baseline': self._calculate_co2_savings(df),
            'green_score_distribution': {
                'excellent': len(df[df['green_score'] >= 80]),
                'good': len(df[(df['green_score'] >= 60) & (df['green_score'] < 80)]),
                'average': len(df[(df['green_score'] >= 40) & (df['green_score'] < 60)]),
                'poor': len(df[df['green_score'] < 40])
            },
            'vehicle_type_distribution': vehicle_distribution,
            'carbon_offset_cost_usd': round(df['total_co2_kg'].sum() * 0.02, 2)
        }
    
    def _calculate_trend_metrics(self, route_data: List[Dict], hours: int) -> Dict:
        """Calculate trend analysis over time"""
        if not route_data:
            return {}
        
        df = pd.DataFrame(route_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Group by time periods
        if hours <= 24:
            df['period'] = df['timestamp'].dt.hour
            period_label = 'hour'
        elif hours <= 168:
            df['period'] = df['timestamp'].dt.day
            period_label = 'day'
        else:
            df['period'] = df['timestamp'].dt.week
            period_label = 'week'
        
        trends = df.groupby('period').agg({
            'total_distance_km': 'mean',
            'total_co2_kg': 'mean',
            'green_score': 'mean',
            'total_time_minutes': 'mean'
        }).round(2)
        
        return {
            'period_type': period_label,
            'distance_trend': trends['total_distance_km'].to_dict(),
            'emissions_trend': trends['total_co2_kg'].to_dict(),
            'green_score_trend': trends['green_score'].to_dict(),
            'time_trend': trends['total_time_minutes'].to_dict()
        }
    
    def _calculate_performance_metrics(self, route_data: List[Dict]) -> Dict:
        """Calculate performance benchmarks and comparisons"""
        if not route_data:
            return {}
        
        df = pd.DataFrame(route_data)
        
        # Performance percentiles
        metrics = ['total_distance_km', 'total_time_minutes', 'total_co2_kg', 'green_score']
        percentiles = {}
        
        for metric in metrics:
            percentiles[metric] = {
                'p25': round(df[metric].quantile(0.25), 2),
                'p50': round(df[metric].quantile(0.50), 2),
                'p75': round(df[metric].quantile(0.75), 2),
                'p90': round(df[metric].quantile(0.90), 2)
            }
        
        return {
            'performance_percentiles': percentiles,
            'top_performing_routes': self._get_top_routes(df),
            'improvement_opportunities': self._identify_improvements(df)
        }
    
    def _calculate_time_savings(self, df: pd.DataFrame) -> float:
        """Calculate time savings vs baseline (estimated)"""
        # Assume baseline is 20% longer than optimized routes
        baseline_time = df['total_time_minutes'].sum() * 1.2
        actual_time = df['total_time_minutes'].sum()
        savings_percentage = ((baseline_time - actual_time) / baseline_time) * 100
        return round(savings_percentage, 1)
    
    def _calculate_distance_optimization(self, df: pd.DataFrame) -> float:
        """Calculate distance optimization ratio"""
        # Estimate optimization ratio based on stops and distance
        avg_optimization = 0.85  # Assume 15% distance reduction on average
        return round(avg_optimization, 2)
    
    def _calculate_co2_savings(self, df: pd.DataFrame) -> float:
        """Calculate CO2 savings vs baseline"""
        # Assume baseline emissions are 25% higher
        baseline_co2 = df['total_co2_kg'].sum() * 1.25
        actual_co2 = df['total_co2_kg'].sum()
        return round(baseline_co2 - actual_co2, 2)
    
    def _get_top_routes(self, df: pd.DataFrame) -> List[Dict]:
        """Get top performing routes"""
        # Sort by green score and select top 3
        top_routes = df.nlargest(3, 'green_score')[['route_id', 'green_score', 'total_co2_kg']].to_dict('records')
        return top_routes
    
    def _identify_improvements(self, df: pd.DataFrame) -> List[str]:
        """Identify improvement opportunities"""
        improvements = []
        
        # Check for high emission routes
        high_emission_routes = len(df[df['total_co2_kg'] > df['total_co2_kg'].quantile(0.8)])
        if high_emission_routes > 0:
            improvements.append(f"{high_emission_routes} routes have high emissions - consider vehicle upgrades")
        
        # Check for long routes
        long_routes = len(df[df['total_time_minutes'] > 300])
        if long_routes > 0:
            improvements.append(f"{long_routes} routes exceed 5 hours - consider route splitting")
        
        # Check vehicle mix
        diesel_percentage = (df['vehicle_type'] == 'diesel_truck').mean() * 100
        if diesel_percentage > 70:
            improvements.append("High diesel vehicle usage - consider electric/hybrid alternatives")
        
        return improvements[:3]
    
    def _extract_route_metrics(self, route_data: Dict, metrics: List[str]) -> Dict:
        """Extract specified metrics from route data"""
        extracted = {}
        
        metric_mapping = {
            'time': 'total_time_minutes',
            'distance': 'total_distance_km',
            'fuel': 'fuel_consumed_liters',
            'emissions': 'total_co2_kg'
        }
        
        for metric in metrics:
            if metric in metric_mapping:
                key = metric_mapping[metric]
                if hasattr(route_data, 'metrics') and key in route_data.metrics:
                    extracted[metric] = route_data.metrics[key]
                else:
                    extracted[metric] = 0
        
        return extracted
    
    def _find_best_performers(self, route_details: Dict, metrics: List[str]) -> Dict:
        """Find best performing routes for each metric"""
        best_performers = {}
        
        for metric in metrics:
            best_route = None
            best_value = float('inf')
            
            for route_id, route_data in route_details.items():
                if metric in route_data and route_data[metric] < best_value:
                    best_value = route_data[metric]
                    best_route = route_id
            
            if best_route:
                best_performers[metric] = {
                    'route_id': best_route,
                    'value': best_value
                }
        
        return best_performers
    
    def _calculate_statistical_summary(self, route_details: Dict, metrics: List[str]) -> Dict:
        """Calculate statistical summary for comparison metrics"""
        summary = {}
        
        for metric in metrics:
            values = [route_data.get(metric, 0) for route_data in route_details.values()]
            
            if values:
                summary[metric] = {
                    'mean': round(np.mean(values), 2),
                    'std': round(np.std(values), 2),
                    'min': round(min(values), 2),
                    'max': round(max(values), 2),
                    'range': round(max(values) - min(values), 2)
                }
        
        return summary
    
    def _generate_comparison_recommendations(self, route_details: Dict, metrics: List[str]) -> List[str]:
        """Generate recommendations based on route comparison"""
        recommendations = []
        
        if 'emissions' in metrics:
            recommendations.append("Focus on routes with highest emissions for vehicle upgrades")
        
        if 'time' in metrics:
            recommendations.append("Analyze time-efficient routes to identify best practices")
        
        if 'distance' in metrics:
            recommendations.append("Review distance variations to optimize route planning")
        
        recommendations.append("Implement learnings from best-performing routes across fleet")
        
        return recommendations