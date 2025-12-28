# FedxSmart System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FedxSmart Platform                      │
├─────────────────────────────────────────────────────────────────┤
│                     Presentation Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Dashboard     │  │   Mobile App    │  │   API Gateway   │ │
│  │   (Web UI)      │  │   (Future)      │  │   (REST/GraphQL)│ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      API Layer                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Route API      │  │ Analytics API   │  │ Scenario API    │ │
│  │  /optimize      │  │ /dashboard      │  │ /what-if        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Route Optimizer │  │ Emission Calc   │  │ Analytics Eng   │ │
│  │ • OR-Tools      │  │ • CO₂ Models    │  │ • KPI Tracking  │ │
│  │ • Real-time     │  │ • Green Score   │  │ • Benchmarking  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Scenario Analyzer│ │ Cache Manager   │  │ External APIs   │ │
│  │ • What-if       │  │ • Redis         │  │ • TomTom        │ │
│  │ • Comparisons   │  │ • Route Cache   │  │ • Weather       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      Data Layer                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   SQLite DB     │  │   Redis Cache   │  │  File Storage   │ │
│  │ • Route Data    │  │ • API Cache     │  │ • Logs          │ │
│  │ • Analytics     │  │ • Session Data  │  │ • Exports       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Component Details

### **Presentation Layer**

#### Web Dashboard

- **Technology**: HTML5, Bootstrap 5, JavaScript, Leaflet Maps
- **Features**:
  - Real-time route visualization
  - Interactive optimization controls
  - Sustainability metrics display
  - Scenario analysis interface
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: WebSocket connections for live data

#### API Gateway

- **Technology**: Flask with CORS support
- **Authentication**: API key validation (production)
- **Rate Limiting**: 100 req/min per IP
- **Documentation**: OpenAPI/Swagger specs
- **Monitoring**: Request logging and metrics

### **API Layer**

#### Route Optimization API

```python
POST /api/optimize-route
{
  "origin": {"lat": 40.7128, "lng": -74.0060},
  "destinations": [
    {"lat": 40.7589, "lng": -73.9851, "priority": 1}
  ],
  "vehicle_type": "diesel_truck",
  "constraints": {"max_capacity": 1000},
  "preferences": {"optimize_for": "time"}
}
```

#### Analytics API

```python
GET /api/analytics/dashboard?time_range=24h
GET /api/emissions/{route_id}
POST /api/analytics/comparison
```

#### Scenario Analysis API

```python
POST /api/scenario-analysis
{
  "base_route_id": "route_123",
  "scenarios": [
    {
      "name": "peak_traffic",
      "conditions": {"traffic_multiplier": 1.5}
    }
  ]
}
```

### **Business Logic Layer**

#### Route Optimizer Service

- **Algorithm**: Google OR-Tools VRP solver
- **Fallback**: Nearest neighbor heuristic
- **Real-time Data**: Traffic, weather integration
- **Constraints**: Vehicle capacity, time windows, distance limits
- **Multi-objective**: Time, distance, fuel, emissions optimization

```python
class RouteOptimizer:
    def optimize(self, origin, destinations, vehicle_type, constraints, preferences):
        # Get real-time conditions
        traffic_data = self._get_traffic_conditions()
        weather_data = self._get_weather_conditions()

        # Build optimization matrices
        distance_matrix, time_matrix = self._build_matrices()

        # Solve VRP with OR-Tools
        optimized_sequence = self._solve_vrp()

        # Return optimized route with metrics
        return OptimizationResult(...)
```

#### Emission Calculator Service

- **Emission Factors**: EPA-certified vehicle emission data
- **Real-time Adjustments**: Traffic congestion, weather impact
- **Green Scoring**: 0-100 sustainability rating
- **Equivalent Metrics**: Trees needed, carbon offset costs

```python
class EmissionCalculator:
    def calculate_route_emissions(self, route, vehicle_type):
        # Base emissions from distance
        base_emissions = distance * emission_factor

        # Traffic impact on emissions
        traffic_emissions = self._calculate_traffic_emissions()

        # Idle time emissions
        idle_emissions = self._calculate_idle_emissions()

        # Generate green score and recommendations
        return EmissionResult(...)
```

#### Analytics Engine Service

- **KPI Tracking**: Route performance, cost savings, emissions
- **Trend Analysis**: Time-series analysis of key metrics
- **Benchmarking**: Industry comparison and best practices
- **Reporting**: Automated dashboard and export capabilities

### **Data Layer**

#### Database Schema

```sql
-- Routes table
CREATE TABLE routes (
    id TEXT PRIMARY KEY,
    origin_lat REAL,
    origin_lng REAL,
    vehicle_type TEXT,
    total_distance REAL,
    total_time REAL,
    total_emissions REAL,
    created_at TIMESTAMP
);

-- Route stops table
CREATE TABLE route_stops (
    id INTEGER PRIMARY KEY,
    route_id TEXT,
    sequence INTEGER,
    lat REAL,
    lng REAL,
    service_time INTEGER,
    FOREIGN KEY (route_id) REFERENCES routes(id)
);

-- Analytics table
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY,
    metric_name TEXT,
    metric_value REAL,
    time_period TEXT,
    recorded_at TIMESTAMP
);
```

#### Caching Strategy

- **Route Cache**: 24-hour TTL for optimization results
- **API Cache**: 5-minute TTL for external API data
- **Analytics Cache**: 1-hour TTL for dashboard metrics
- **Cache Invalidation**: Event-driven cache updates

## 🔄 Data Flow

### **Route Optimization Flow**

```
1. User Input → API Gateway → Route Optimizer
2. Route Optimizer → External APIs (Traffic, Weather)
3. Route Optimizer → OR-Tools Solver
4. Solver Results → Emission Calculator
5. Combined Results → Cache → User Interface
```

### **Real-time Data Integration**

```
External APIs → Cache Manager → Business Services
     ↓              ↓              ↓
TomTom Traffic → Redis Cache → Route Optimizer
Weather API   → Redis Cache → Emission Calculator
OSRM Routing  → Redis Cache → Analytics Engine
```

## 🚀 Deployment Architecture

### **Development Environment**

```yaml
# docker-compose.yml
services:
  fedx-smart:
    build: .
    ports: ["5000:5000"]
    environment:
      - DEBUG=True
      - REDIS_URL=redis://redis:6379

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```

### **Production Environment**

```yaml
# Production deployment
services:
  app:
    image: fedx-smart:latest
    replicas: 3
    resources:
      limits: { memory: 512M, cpus: 0.5 }

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]

  redis:
    image: redis:7-alpine
    volumes: [redis_data:/data]

  monitoring:
    image: prometheus:latest
```

### **Scaling Strategy**

- **Horizontal Scaling**: Multiple app instances behind load balancer
- **Database Scaling**: Read replicas for analytics queries
- **Cache Scaling**: Redis cluster for high availability
- **CDN Integration**: Static asset delivery optimization

## 🔒 Security Architecture

### **API Security**

- **Authentication**: JWT tokens or API keys
- **Authorization**: Role-based access control (RBAC)
- **Rate Limiting**: Per-user and per-IP limits
- **Input Validation**: Schema validation for all inputs
- **HTTPS**: TLS 1.3 encryption for all communications

### **Data Security**

- **Encryption at Rest**: AES-256 database encryption
- **Encryption in Transit**: TLS for all API calls
- **Data Anonymization**: PII scrubbing in logs
- **Audit Logging**: Complete API access logging
- **Backup Security**: Encrypted backup storage

### **Infrastructure Security**

- **Container Security**: Minimal base images, security scanning
- **Network Security**: VPC isolation, security groups
- **Secrets Management**: Environment-based secret injection
- **Monitoring**: Real-time security event monitoring

## 📊 Performance Specifications

### **Response Time Requirements**

- **Route Optimization**: < 5 seconds for 50 stops
- **Dashboard Loading**: < 2 seconds initial load
- **API Responses**: < 500ms for cached data
- **Map Rendering**: < 1 second for route visualization

### **Throughput Specifications**

- **Concurrent Users**: 100+ simultaneous users
- **API Requests**: 1000+ requests per minute
- **Route Optimizations**: 50+ concurrent optimizations
- **Data Processing**: 10,000+ routes per hour

### **Scalability Targets**

- **Routes per Day**: 10,000+ optimization requests
- **Data Storage**: 1TB+ route and analytics data
- **Geographic Coverage**: Global deployment capability
- **Fleet Size**: 1,000+ vehicles per organization

## 🔍 Monitoring & Observability

### **Application Monitoring**

- **Metrics**: Response times, error rates, throughput
- **Logging**: Structured JSON logging with correlation IDs
- **Tracing**: Distributed tracing for request flows
- **Alerting**: Automated alerts for performance degradation

### **Business Metrics**

- **Route Optimization Success Rate**: > 99%
- **Average Time Savings**: 30-40% vs baseline
- **Emission Reduction**: 25-50% depending on vehicle mix
- **Cost Savings**: $50-100 per optimized route

### **Infrastructure Monitoring**

- **Resource Usage**: CPU, memory, disk, network
- **Database Performance**: Query times, connection pools
- **Cache Performance**: Hit rates, eviction rates
- **External API Health**: Response times, error rates

## 🔧 Technology Stack Summary

### **Backend Technologies**

- **Language**: Python 3.9+
- **Framework**: Flask with Gunicorn
- **Optimization**: Google OR-Tools
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Cache**: Redis
- **APIs**: RESTful with JSON

### **Frontend Technologies**

- **UI Framework**: Bootstrap 5
- **Maps**: Leaflet.js with OpenStreetMap
- **Charts**: Chart.js for analytics
- **Real-time**: WebSocket connections
- **Mobile**: Responsive design

### **DevOps & Infrastructure**

- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

### **External Integrations**

- **Routing**: TomTom API, Google Maps API, OSRM
- **Weather**: OpenWeatherMap API
- **Traffic**: TomTom Traffic API
- **Air Quality**: AQICN API (optional)

---

This architecture provides a solid foundation for enterprise-scale route optimization with sustainability intelligence, designed to handle FedEx's operational requirements while maintaining high performance and reliability.
