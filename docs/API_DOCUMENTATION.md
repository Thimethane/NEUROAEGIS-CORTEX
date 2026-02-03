# 🔌 AegisAI API Documentation

Complete API reference for AegisAI backend services.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
- [WebSocket](#websocket)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## 🌐 Overview

The AegisAI API provides programmatic access to:
- **Video Analysis**: AI-powered threat detection
- **Incident Management**: CRUD operations on incidents
- **System Monitoring**: Health checks and statistics
- **Action Execution**: Automated response handling

### API Characteristics

- **Protocol**: REST over HTTP/HTTPS
- **Format**: JSON
- **Authentication**: API Key (optional)
- **CORS**: Enabled for whitelisted origins
- **Rate Limiting**: 100 requests/minute per IP

---

## 🔐 Authentication

### API Key (Optional)

For production deployments, protect your API:

```bash
# Add to backend/.env
API_KEY=your_secure_api_key_here
REQUIRE_API_KEY=true
```

**Usage:**

```bash
curl -H "X-API-Key: your_secure_api_key_here" \
  http://localhost:8000/api/incidents
```

**Headers:**
```
X-API-Key: your_secure_api_key_here
```

---

## 🌍 Base URL

### Development
```
http://localhost:8000
```

### Production
```
https://your-backend.onrender.com
```

### API Documentation (Swagger)
```
http://localhost:8000/docs
```

### Alternative Docs (ReDoc)
```
http://localhost:8000/redoc
```

---

## 📡 Endpoints

### System Endpoints

#### Get API Info

```http
GET /
```

**Description**: Returns API information and version.

**Response:**
```json
{
  "name": "AegisAI",
  "version": "2.5.0",
  "description": "Autonomous Security & Incident Response Agent",
  "docs": "/docs"
}
```

**Example:**
```bash
curl http://localhost:8000/
```

---

#### Health Check

```http
GET /health
```

**Description**: Check system health status.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "database": "ok",
    "vision_agent": "ok",
    "planner_agent": "ok"
  },
  "timestamp": "2025-01-19T10:30:00Z",
  "uptime_seconds": 3600
}
```

**Status Codes:**
- `200 OK` - All systems operational
- `503 Service Unavailable` - One or more components unhealthy

**Example:**
```bash
curl http://localhost:8000/health
```

---

### Analysis Endpoints

#### Analyze Frame

```http
POST /api/analyze
```

**Description**: Analyze a single video frame for threats.

**Request Body:**
```json
{
  "image": "base64_encoded_image_string",
  "frame_number": 42,
  "timestamp": "2025-01-19T10:30:00Z",
  "metadata": {
    "camera_id": "CAM_01",
    "location": "Main Entrance"
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | string | Yes | Base64-encoded JPEG/PNG image |
| `frame_number` | integer | No | Sequential frame identifier |
| `timestamp` | string | No | ISO 8601 timestamp |
| `metadata` | object | No | Additional context |

**Response:**
```json
{
  "incident": true,
  "type": "suspicious_behavior",
  "severity": "medium",
  "confidence": 82.5,
  "reasoning": "Individual exhibiting nervous behavior and repeatedly glancing at camera. Hands concealed. Unusual loitering pattern detected.",
  "subjects": [
    {
      "description": "Person in dark hoodie",
      "behavior": "Nervous movements",
      "location": "Near entrance"
    }
  ],
  "recommended_actions": [
    "Increase camera focus on subject",
    "Alert security personnel",
    "Record interaction for review"
  ],
  "timestamp": "2025-01-19T10:30:00Z",
  "processing_time_ms": 1250
}
```

**Status Codes:**
- `200 OK` - Analysis successful
- `400 Bad Request` - Invalid image format
- `422 Unprocessable Entity` - Missing required fields
- `500 Internal Server Error` - Analysis failed

**Example:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "frame_number": 1
  }'
```

---

### Incident Management

#### List Incidents

```http
GET /api/incidents
```

**Description**: Retrieve all incidents with optional filtering.

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by status | `active`, `resolved`, `false_positive` |
| `severity` | string | Filter by severity | `low`, `medium`, `high`, `critical` |
| `type` | string | Filter by incident type | `violence`, `suspicious_behavior` |
| `from_date` | string | Start date (ISO 8601) | `2025-01-01T00:00:00Z` |
| `to_date` | string | End date (ISO 8601) | `2025-01-31T23:59:59Z` |
| `limit` | integer | Max results (default: 100) | `50` |
| `offset` | integer | Pagination offset | `0` |

**Response:**
```json
{
  "total": 150,
  "incidents": [
    {
      "id": "incident_123",
      "timestamp": "2025-01-19T10:30:00Z",
      "type": "suspicious_behavior",
      "severity": "medium",
      "confidence": 82.5,
      "status": "active",
      "reasoning": "...",
      "subjects": [...],
      "response_plan": [...],
      "evidence_path": "/evidence/2025-01-19/incident_123.jpg",
      "created_at": "2025-01-19T10:30:01Z",
      "updated_at": "2025-01-19T10:30:01Z"
    }
  ],
  "pagination": {
    "limit": 100,
    "offset": 0,
    "has_more": true
  }
}
```

**Example:**
```bash
# All incidents
curl http://localhost:8000/api/incidents

# Active high-severity incidents
curl "http://localhost:8000/api/incidents?status=active&severity=high"

# Incidents from last 24 hours
curl "http://localhost:8000/api/incidents?from_date=2025-01-18T10:00:00Z"
```

---

#### Get Incident by ID

```http
GET /api/incidents/{incident_id}
```

**Description**: Retrieve a specific incident.

**Path Parameters:**
- `incident_id` (string, required): Incident identifier

**Response:**
```json
{
  "id": "incident_123",
  "timestamp": "2025-01-19T10:30:00Z",
  "type": "violence",
  "severity": "high",
  "confidence": 95.0,
  "status": "active",
  "reasoning": "Weapon detected...",
  "subjects": [...],
  "response_plan": [...],
  "evidence_path": "/evidence/incident_123.jpg",
  "actions_taken": [
    {
      "action": "alert_authorities",
      "status": "completed",
      "timestamp": "2025-01-19T10:30:05Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Incident found
- `404 Not Found` - Incident doesn't exist

**Example:**
```bash
curl http://localhost:8000/api/incidents/incident_123
```

---

#### Update Incident Status

```http
POST /api/incidents/{incident_id}/status
```

**Description**: Update incident status (resolve, escalate, etc.).

**Request Body:**
```json
{
  "status": "resolved",
  "notes": "False alarm - authorized personnel",
  "resolved_by": "operator_42"
}
```

**Status Values:**
- `active` - Incident ongoing
- `investigating` - Under review
- `resolved` - Resolved/completed
- `false_positive` - Not an actual incident
- `escalated` - Escalated to authorities

**Response:**
```json
{
  "id": "incident_123",
  "status": "resolved",
  "updated_at": "2025-01-19T10:45:00Z",
  "notes": "False alarm - authorized personnel"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/incidents/incident_123/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "notes": "False alarm"
  }'
```

---

#### Delete Old Incidents

```http
DELETE /api/incidents/cleanup
```

**Description**: Delete incidents older than specified days.

**Query Parameters:**
- `days` (integer, default: 30): Delete incidents older than this many days

**Response:**
```json
{
  "deleted_count": 45,
  "message": "Deleted 45 incidents older than 30 days"
}
```

**Example:**
```bash
# Delete incidents older than 30 days
curl -X DELETE "http://localhost:8000/api/incidents/cleanup?days=30"

# Delete incidents older than 7 days
curl -X DELETE "http://localhost:8000/api/incidents/cleanup?days=7"
```

---

### Statistics Endpoints

#### Get System Statistics

```http
GET /api/stats
```

**Description**: Get overall system statistics.

**Response:**
```json
{
  "total_incidents": 150,
  "active_incidents": 5,
  "incidents_today": 12,
  "incidents_this_week": 45,
  "incidents_by_severity": {
    "low": 80,
    "medium": 50,
    "high": 15,
    "critical": 5
  },
  "incidents_by_type": {
    "violence": 10,
    "suspicious_behavior": 85,
    "intrusion": 30,
    "vandalism": 15,
    "normal": 10
  },
  "average_confidence": 78.5,
  "false_positive_rate": 0.08,
  "response_time_avg_ms": 1250
}
```

**Example:**
```bash
curl http://localhost:8000/api/stats
```

---

#### Get Agent Statistics

```http
GET /api/agents/stats
```

**Description**: Get AI agent performance metrics.

**Response:**
```json
{
  "vision_agent": {
    "agent": "VisionAgent",
    "total_calls": 1500,
    "total_errors": 12,
    "error_rate": 0.008,
    "avg_response_time_ms": 1200,
    "uptime_hours": 24.5
  },
  "planner_agent": {
    "agent": "PlannerAgent",
    "total_calls": 150,
    "total_errors": 2,
    "error_rate": 0.013,
    "avg_response_time_ms": 800,
    "uptime_hours": 24.5
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/agents/stats
```

---

### Action Endpoints

#### Execute Action

```http
POST /api/actions/execute
```

**Description**: Manually execute a response action.

**Request Body:**
```json
{
  "action_type": "alert_security",
  "incident_id": "incident_123",
  "parameters": {
    "urgency": "high",
    "message": "Immediate response required"
  }
}
```

**Action Types:**
- `alert_security` - Notify security personnel
- `alert_authorities` - Contact law enforcement
- `lock_doors` - Engage security locks
- `sound_alarm` - Activate alarm system
- `record_evidence` - Save video evidence
- `increase_monitoring` - Enhance surveillance

**Response:**
```json
{
  "action_id": "action_456",
  "status": "completed",
  "result": {
    "notification_sent": true,
    "recipients": ["security@example.com"],
    "timestamp": "2025-01-19T10:30:10Z"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/actions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "alert_security",
    "incident_id": "incident_123",
    "parameters": {"urgency": "high"}
  }'
```

---

## 🔌 WebSocket

### Real-time Analysis Stream

```
ws://localhost:8000/ws/analysis
```

**Description**: Stream real-time analysis results.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analysis');

ws.onopen = () => {
  console.log('Connected to analysis stream');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Analysis result:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from stream');
};
```

**Message Format:**
```json
{
  "type": "analysis_result",
  "data": {
    "incident": true,
    "type": "suspicious_behavior",
    "severity": "medium",
    "confidence": 82.5,
    "timestamp": "2025-01-19T10:30:00Z"
  }
}
```

**Message Types:**
- `analysis_result` - New analysis completed
- `incident_created` - New incident saved
- `incident_updated` - Incident status changed
- `system_status` - Health status update
- `error` - Error occurred

---

## ⚠️ Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_IMAGE",
    "message": "Image data is not valid base64",
    "details": {
      "field": "image",
      "received_type": "string",
      "expected_format": "base64"
    }
  },
  "timestamp": "2025-01-19T10:30:00Z",
  "request_id": "req_abc123"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | System unhealthy |

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_API_KEY` | API key is invalid | Check your API key |
| `INVALID_IMAGE` | Image format invalid | Ensure proper base64 encoding |
| `ANALYSIS_FAILED` | AI analysis failed | Retry or check logs |
| `INCIDENT_NOT_FOUND` | Incident doesn't exist | Verify incident ID |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait before retrying |

---

## 🚦 Rate Limiting

### Default Limits

- **100 requests/minute** per IP address
- **1000 requests/hour** per API key
- **10 concurrent WebSocket connections**

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705658400
```

### Handling Rate Limits

```javascript
async function analyzeWithRetry(imageData, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: JSON.stringify({ image: imageData })
      });
      
      if (response.status === 429) {
        const resetTime = response.headers.get('X-RateLimit-Reset');
        const waitMs = (resetTime * 1000) - Date.now();
        await new Promise(resolve => setTimeout(resolve, waitMs));
        continue;
      }
      
      return await response.json();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
}
```

---

## 💡 Examples

### Complete Analysis Workflow

```javascript
// 1. Check system health
const healthCheck = await fetch('http://localhost:8000/health');
const health = await healthCheck.json();

if (health.status !== 'healthy') {
  console.error('System not healthy');
  return;
}

// 2. Capture and encode frame
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
ctx.drawImage(videoElement, 0, 0);
const imageData = canvas.toDataURL('image/jpeg').split(',')[1];

// 3. Analyze frame
const analysisResponse = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    image: imageData,
    frame_number: frameCount++,
    timestamp: new Date().toISOString()
  })
});

const result = await analysisResponse.json();

// 4. Handle incident
if (result.incident) {
  console.log(`Incident detected: ${result.type}`);
  
  // Get full incident details
  const incidentResponse = await fetch(
    `http://localhost:8000/api/incidents/${result.incident_id}`
  );
  const incident = await incidentResponse.json();
  
  // Update UI
  displayIncident(incident);
  
  // Execute recommended actions
  for (const action of result.recommended_actions) {
    await executeAction(action, incident.id);
  }
}
```

### Batch Analysis

```python
import asyncio
import aiohttp
import base64

async def analyze_batch(image_paths: list[str]):
    """Analyze multiple images concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for i, path in enumerate(image_paths):
            with open(path, 'rb') as f:
                image_b64 = base64.b64encode(f.read()).decode()
            
            task = session.post(
                'http://localhost:8000/api/analyze',
                json={
                    'image': image_b64,
                    'frame_number': i
                }
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        results = [await r.json() for r in responses]
        
        return results

# Usage
results = asyncio.run(analyze_batch([
    'frame1.jpg',
    'frame2.jpg',
    'frame3.jpg'
]))
```

---

## 📚 Additional Resources

- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Postman Collection**: [Download](./postman_collection.json)
- **Code Examples**: [GitHub Examples](https://github.com/Thimethane/aegisai/tree/main/examples)

---

**Last Updated**: January 2026  
**API Version**: 2.5.0