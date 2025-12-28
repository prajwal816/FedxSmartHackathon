"""
Data models for emission calculations and sustainability metrics
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class VehicleSpec:
    """Vehicle specification for emission calculations"""
    vehicle_type: str
    fuel_type: str
    emission_factor: float  # kg CO2 per km
    idle_emission_rate: float  # kg CO2 per hour
    cold_start_penalty: float  # kg CO2 per start
    efficiency_rating: str  # A+, A, B+, B, C, D
    description: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class EmissionBreakdown:
    """Detailed breakdown of emissions by source"""
    base_driving: float  # kg CO2 from normal driving
    traffic_congestion: float  # kg CO2 from traffic delays
    idle_time: float  # kg CO2 from idling at stops
    cold_start: float  # kg CO2 from engine cold start
    total: float  # Total emissions
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class EquivalentMetrics:
    """Environmental equivalent metrics for context"""
    trees_needed_per_year: float  # Trees needed to offset CO2
    equivalent_car_km: float  # Equivalent passenger car kilometers
    equivalent_gasoline_liters: float  # Equivalent gasoline consumption
    carbon_offset_cost_usd: float  # Cost to offset carbon emissions
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class EmissionResult:
    """Complete emission calculation result"""
    total_co2_kg: float
    co2_per_km: float
    green_score: int  # 0-100, higher is better
    emission_breakdown: EmissionBreakdown
    vehicle_type: str
    distance_km: float
    equivalent_metrics: EquivalentMetrics
    recommendations: List[str]
    calculation_timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            'total_co2_kg': self.total_co2_kg,
            'co2_per_km': self.co2_per_km,
            'green_score': self.green_score,
            'emission_breakdown': self.emission_breakdown.to_dict(),
            'vehicle_type': self.vehicle_type,
            'distance_km': self.distance_km,
            'equivalent_metrics': self.equivalent_metrics.to_dict(),
            'recommendations': self.recommendations,
            'calculation_timestamp': self.calculation_timestamp.isoformat()
        }

@dataclass
class SustainabilityMetrics:
    """Comprehensive sustainability metrics"""
    carbon_footprint_kg: float
    carbon_intensity_kg_per_km: float
    fuel_efficiency_km_per_liter: float
    renewable_energy_percentage: float
    green_score: int
    sustainability_rating: str  # 'Excellent', 'Good', 'Average', 'Poor'
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class EmissionComparison:
    """Comparison of emissions between different scenarios"""
    baseline_emissions: float
    optimized_emissions: float
    absolute_reduction: float
    percentage_reduction: float
    cost_savings_usd: float
    environmental_impact: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class CarbonOffset:
    """Carbon offset information"""
    emissions_to_offset_kg: float
    offset_cost_usd: float
    offset_projects: List[str]
    verification_standard: str
    offset_timeline_years: int
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class EnvironmentalImpact:
    """Broader environmental impact assessment"""
    co2_emissions_kg: float
    nox_emissions_g: float
    pm_emissions_g: float
    noise_pollution_db: float
    air_quality_impact: str
    ecosystem_impact_score: int  # 0-100
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class GreenAlternative:
    """Alternative green transportation option"""
    alternative_type: str  # 'electric', 'hybrid', 'hydrogen', 'rail', 'multimodal'
    emission_reduction_kg: float
    emission_reduction_percentage: float
    additional_cost_usd: float
    implementation_complexity: str  # 'Low', 'Medium', 'High'
    payback_period_months: int
    infrastructure_requirements: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class EmissionTrend:
    """Emission trends over time"""
    period: str  # 'daily', 'weekly', 'monthly'
    emissions_data: List[float]  # Time series of emissions
    trend_direction: str  # 'improving', 'stable', 'worsening'
    average_reduction_rate: float  # Percentage per period
    target_emissions: float
    target_achievement_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        if self.target_achievement_date:
            result['target_achievement_date'] = self.target_achievement_date.isoformat()
        return result