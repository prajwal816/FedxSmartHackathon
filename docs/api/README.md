# FedxSmart API Documentation

## Overview
The FedxSmart API provides endpoints for route optimization, emission calculation, and analytics.

## Authentication
Currently, no authentication is required for demo purposes. In production, implement API key authentication.

## Endpoints

### Route Optimization
- **POST** `/api/optimize-route`
- **GET** `/api/emissions/{route_id}`
- **POST** `/api/scenario-analysis`

### Analytics
- **GET** `/api/analytics/dashboard`
- **POST** `/api/analytics/comparison`

### Utilities
- **GET** `/api/vehicles`
- **GET** `/health`

## Rate Limits
- 100 requests per minute per IP
- 1000 requests per hour per IP

## Error Handling
All errors return JSON with error message and appropriate HTTP status code.
