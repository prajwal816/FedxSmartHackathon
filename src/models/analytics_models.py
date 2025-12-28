"""
Data models for analytics and reporting
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class DashboardMetrics:
    """Key metrics for dashboard display"""
    total_routes: int
    total_distance_km: float
    total_emissions_kg: float
    average_green_score: float
    fuel_savings_percentage: float
    time_savings_percentage: float
    cost_savings_usd: float
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class PerformanceMetrics:
    """Performance metrics for route optimization"""
    optimization_time_seconds: float
    success_rate_percentage: float
    average_improvement_percentage: float
    routes_optimized_count: int
    api_response_time_ms: float
    cache_hit_rate_percentage: float
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class RouteComparison:
    """Comparison data between routes"""
    route_ids: List[str]
    metrics: Dict[str, List[float]]  # metric_name -> [values for each route]
    best_performers: Dict[str, str]  # metric_name -> best_route_id
    statistical_summary: Dict[str, Dict[str, float]]  # metric -> {mean, std, min, max}
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class TrendAnalysis:
    """Trend analysis over time periods"""
    period_type: str  # 'hourly', 'daily', 'weekly', 'monthly'
    metrics: Dict[str, List[float]]  # metric_name -> time series values
    trend_directions: Dict[str, str]  # metric_name -> 'improving'/'stable'/'declining'
    growth_rates: Dict[str, float]  # metric_name -> percentage change per period
    seasonality_detected: bool
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class EfficiencyAnalysis:
    """Analysis of operational efficiency"""
    vehicle_utilization_percentage: float
    route_density_stops_per_km: float
    time_efficiency_percentage: float
    fuel_efficiency_km_per_liter: float
    cost_per_delivery_usd: float
    delivery_success_rate_percentage: float
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class SustainabilityReport:
    """Comprehensive sustainability reporting"""
    total_co2_reduction_kg: float
    percentage_improvement: float
    green_vehicle_adoption_rate: float
    carbon_offset_cost_usd: float
    environmental_score: int  # 0-100
    sustainability_goals_progress: Dict[str, float]  # goal_name -> progress_percentage
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class CostAnalysis:
    """Financial analysis of route optimization"""
    total_cost_usd: float
    fuel_cost_usd: float
    labor_cost_usd: float
    vehicle_maintenance_cost_usd: float
    cost_per_km: float
    cost_per_delivery: float
    savings_vs_baseline_usd: float
    roi_percentage: float
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class OperationalInsights:
    """Operational insights and recommendations"""
    peak_delivery_hours: List[str]
    optimal_vehicle_mix: Dict[str, int]  # vehicle_type -> recommended_count
    route_optimization_opportunities: List[str]
    capacity_utilization_insights: List[str]
    seasonal_patterns: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class KPIReport:
    """Key Performance Indicators report"""
    delivery_time_performance: float  # Percentage on-time deliveries
    fuel_efficiency_kpi: float
    emission_reduction_kpi: float
    cost_efficiency_kpi: float
    customer_satisfaction_score: float
    driver_productivity_score: float
    kpi_trends: Dict[str, str]  # kpi_name -> trend_direction
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class BenchmarkComparison:
    """Comparison against industry benchmarks"""
    metric_name: str
    current_value: float
    industry_average: float
    industry_best_practice: float
    performance_percentile: int  # 0-100
    gap_to_best_practice: float
    improvement_potential: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class AlertMetrics:
    """Metrics that trigger alerts or notifications"""
    metric_name: str
    current_value: float
    threshold_value: float
    alert_type: str  # 'warning', 'critical', 'info'
    alert_message: str
    recommended_action: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

@dataclass
class ScenarioImpact:
    """Impact analysis for different scenarios"""
    scenario_name: str
    base_metrics: Dict[str, float]
    scenario_metrics: Dict[str, float]
    impact_analysis: Dict[str, Dict[str, float]]  # metric -> {absolute_change, percentage_change}
    feasibility_score: int  # 0-100
    implementation_cost_usd: float
    expected_roi_months: int
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class DataQualityMetrics:
    """Metrics about data quality and completeness"""
    data_completeness_percentage: float
    data_accuracy_score: int  # 0-100
    real_time_data_availability: float  # Percentage
    api_reliability_percentage: float
    data_freshness_minutes: float
    missing_data_points: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class UserEngagementMetrics:
    """Metrics about user interaction with the system"""
    active_users_count: int
    routes_optimized_per_user: float
    dashboard_views_count: int
    api_calls_count: int
    feature_usage_statistics: Dict[str, int]  # feature_name -> usage_count
    user_satisfaction_score: float
    
    def to_dict(self) -> Dict:
        return asdict(self)