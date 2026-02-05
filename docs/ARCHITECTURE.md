# 🏗️ NEUROAEGIS CORTEX - SYSTEM ARCHITECTURE

## High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React TypeScript UI] --> B[Video Feed Component]
        A --> C[Analysis Dashboard]
        A --> D[Action Panel]
        A --> E[Evidence Gallery]
    end
    
    subgraph "API Layer"
        F[FastAPI Backend] --> G[/api/analyze]
        F --> H[/api/health]
        F --> I[/api/evidence]
        F --> J[/api/stats]
    end
    
    subgraph "AI Processing Layer"
        K[Vision Agent<br/>Gemini 3 Pro] --> L[Frame Analysis]
        M[Planner Agent<br/>Gemini 3 Pro] --> N[Response Planning]
    end
    
    subgraph "Execution Layer"
        O[Action Executor] --> P[Email Alerts]
        O --> Q[SMS Alerts]
        O --> R[IoT Actions]
        O --> S[Evidence Storage]
    end
    
    subgraph "Data Layer"
        T[(SQLite Database)] --> U[Incidents]
        T --> V[Actions]
        T --> W[System Stats]
        X[File System] --> Y[Evidence Images]
    end
    
    subgraph "External Services"
        Z[Google Gemini API]
        AA[SMTP Server]
        AB[Twilio SMS]
    end
    
    B -->|Base64 Image| G
    G -->|Frame Data| K
    K -->|Analysis Result| M
    M -->|Action Plan| O
    O --> T
    O --> X
    
    K -.->|API Calls| Z
    M -.->|API Calls| Z
    O -.->|Email| AA
    O -.->|SMS| AB
    
    C -->|Fetch Stats| J
    E -->|Load Images| I
    
    style K fill:#4285f4
    style M fill:#4285f4
    style Z fill:#ea4335
```

## Detailed Component Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant VisionAgent
    participant Gemini3
    participant PlannerAgent
    participant ActionExecutor
    participant Database
    
    User->>Frontend: Enable monitoring
    Frontend->>Frontend: Start camera capture
    
    loop Every 4 seconds
        Frontend->>Frontend: Capture frame
        Frontend->>Backend: POST /api/analyze (base64 image)
        Backend->>VisionAgent: process(frame)
        VisionAgent->>VisionAgent: Build temporal context
        VisionAgent->>Gemini3: Generate content (image + context)
        Gemini3-->>VisionAgent: JSON response
        VisionAgent->>VisionAgent: Validate & parse
        
        alt Incident Detected
            VisionAgent-->>Backend: Incident analysis
            Backend->>PlannerAgent: process(incident)
            PlannerAgent->>Gemini3: Generate action plan
            Gemini3-->>PlannerAgent: JSON action plan
            PlannerAgent-->>Backend: Validated plan
            
            Backend->>ActionExecutor: execute_plan(plan, incident_id)
            ActionExecutor->>Database: Save incident
            ActionExecutor->>ActionExecutor: Execute actions (alert, save, log)
            
            alt Email Enabled
                ActionExecutor->>SMTP: Send alert
            end
            
            ActionExecutor->>Database: Log actions
            ActionExecutor-->>Backend: Execution complete
        else No Incident
            VisionAgent-->>Backend: Normal analysis
        end
        
        Backend-->>Frontend: Analysis result
        Frontend->>Frontend: Update UI
        Frontend->>User: Display result
    end
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Input"
        A[Camera Feed] --> B[Frame Buffer]
    end
    
    subgraph "Processing Pipeline"
        B --> C{Frame<br/>Sampler}
        C -->|Every 4s| D[Base64<br/>Encoder]
        D --> E[API Request]
        
        E --> F[Vision Agent]
        F --> G{Incident?}
        
        G -->|Yes| H[Planner Agent]
        G -->|No| M[Log Normal]
        
        H --> I[Action Executor]
        I --> J[Save Evidence]
        I --> K[Send Alerts]
        I --> L[Log Incident]
    end
    
    subgraph "Storage"
        J --> N[(Database)]
        J --> O[File System]
        K --> N
        L --> N
        M --> N
    end
    
    subgraph "Output"
        N --> P[Dashboard]
        O --> Q[Evidence Gallery]
        N --> R[Statistics]
    end
    
    style F fill:#4285f4
    style H fill:#4285f4
    style G fill:#ea4335
```

## Technology Stack

```mermaid
graph TB
    subgraph "Frontend Stack"
        A[React 18] --> B[TypeScript 5]
        A --> C[Vite]
        A --> D[TailwindCSS]
    end
    
    subgraph "Backend Stack"
        E[Python 3.11] --> F[FastAPI]
        E --> G[OpenCV]
        E --> H[Google GenAI SDK]
    end
    
    subgraph "AI Models"
        I[Gemini 3 Pro Preview]
        J[gemini-3-pro-preview]
    end
    
    subgraph "Infrastructure"
        K[Docker] --> L[Docker Compose]
        M[SQLite]
        N[Nginx Optional]
    end
    
    A -.->|HTTP| F
    F -.->|API| I
    F --> M
    
    style I fill:#4285f4
    style F fill:#34a853
    style A fill:#fbbc04
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Docker Environment"
        subgraph "Frontend Container"
            A[Nginx] --> B[React Build]
            B --> C[Port 3000]
        end
        
        subgraph "Backend Container"
            D[Uvicorn] --> E[FastAPI App]
            E --> F[Port 8000]
            E --> G[Vision Agent]
            E --> H[Planner Agent]
            E --> I[Action Executor]
        end
        
        subgraph "Storage"
            J[(SQLite DB)]
            K[Evidence Directory]
        end
    end
    
    subgraph "Host Machine"
        L[Camera Device] --> M[/dev/video0]
    end
    
    subgraph "External"
        N[Gemini API]
        O[SMTP Server]
        P[Twilio API]
    end
    
    C -->|Vite Proxy| F
    M -.->|Optional| D
    
    G -.->|HTTPS| N
    H -.->|HTTPS| N
    I -.->|SMTP| O
    I -.->|HTTPS| P
    
    E --> J
    E --> K
    
    style N fill:#4285f4
    style A fill:#34a853
    style D fill:#34a853
```

## Security Architecture

```mermaid
graph TB
    subgraph "Network Layer"
        A[Client Browser] -->|HTTPS| B[Frontend:3000]
        B -->|Vite Proxy| C[Backend:8000]
    end
    
    subgraph "Authentication Layer"
        C --> D{API Key<br/>Validation}
        D -->|Valid| E[Process Request]
        D -->|Invalid| F[403 Forbidden]
    end
    
    subgraph "Processing Layer"
        E --> G[Input Validation]
        G --> H[Sanitize Data]
        H --> I[Process Frame]
    end
    
    subgraph "Data Protection"
        I --> J[Encrypt Sensitive]
        J --> K[(Database)]
        I --> L[Local Storage]
    end
    
    subgraph "External Communication"
        I -.->|Gemini API Key| M[Google Cloud]
        I -.->|SMTP Creds| N[Email Server]
        I -.->|Twilio Creds| O[SMS Service]
    end
    
    style D fill:#ea4335
    style J fill:#fbbc04
```

## Error Handling Flow

```mermaid
graph TB
    A[API Request] --> B{Valid?}
    B -->|No| C[400 Bad Request]
    B -->|Yes| D[Process Frame]
    
    D --> E{Gemini<br/>Available?}
    E -->|No| F[Return Default Result]
    E -->|Yes| G[Call Gemini API]
    
    G --> H{API<br/>Success?}
    H -->|429 Quota| I[Log Error + Return Default]
    H -->|503 Overload| J[Log Warning + Return Default]
    H -->|200 OK| K[Parse Response]
    
    K --> L{Valid<br/>JSON?}
    L -->|No| M[Use Fallback Data]
    L -->|Yes| N[Validate Fields]
    
    N --> O{All Fields<br/>Present?}
    O -->|No| P[Add Missing Fields]
    O -->|Yes| Q[Return Success]
    
    F --> Q
    I --> Q
    J --> Q
    M --> Q
    P --> Q
    
    style H fill:#ea4335
    style O fill:#fbbc04
    style Q fill:#34a853
```

## Agent State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: Frame Received
    
    Processing --> Analyzing: Send to Gemini
    Analyzing --> ValidatingResponse: API Response
    
    ValidatingResponse --> IncidentDetected: incident=true
    ValidatingResponse --> NormalActivity: incident=false
    
    IncidentDetected --> Planning: Generate Plan
    Planning --> ExecutingActions: Plan Ready
    
    ExecutingActions --> SavingEvidence: Step 1
    SavingEvidence --> SendingAlerts: Step 2
    SendingAlerts --> LoggingIncident: Step 3
    LoggingIncident --> Complete: All Actions Done
    
    NormalActivity --> Logging: Record Normal
    Logging --> Complete: Logged
    
    Complete --> UpdateHistory: Add to Context
    UpdateHistory --> Idle: Ready for Next
    
    ValidatingResponse --> ErrorHandling: Validation Failed
    Analyzing --> ErrorHandling: API Error
    ErrorHandling --> DefaultResult: Generate Fallback
    DefaultResult --> Complete: Continue
```

---

## System Specifications

### Performance Characteristics

| Metric | Value |
|--------|-------|
| Average Processing Time | 4.9s per frame |
| Throughput | ~12 frames/minute |
| Latency (end-to-end) | <6s |
| Database Query Time | <10ms |
| Evidence Save Time | <100ms |

### Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4GB | 8GB |
| Disk | 10GB | 50GB+ |
| Network | 10 Mbps | 50+ Mbps |

### Scalability

- **Single Camera:** 12 frames/min
- **Multiple Cameras:** Deploy multiple backend instances
- **Horizontal Scaling:** Add containers as needed
- **Load Balancing:** Nginx for distribution

---

## Key Design Decisions

### 1. Why Microservices Architecture?
- **Modularity:** Easy to upgrade individual components
- **Scalability:** Can scale agents independently
- **Maintainability:** Clear separation of concerns

### 2. Why Docker?
- **Portability:** Works on any platform
- **Isolation:** Dependencies contained
- **Reproducibility:** Same environment everywhere

### 3. Why SQLite?
- **Simplicity:** No separate database server
- **Performance:** Fast for single-node deployments
- **Portability:** Database is a single file

### 4. Why Two AI Agents?
- **Specialization:** Each optimized for its task
- **Flexibility:** Can use different models/versions
- **Clarity:** Separate vision from planning logic

---

**This architecture provides a solid foundation for intelligent, scalable security monitoring powered by Gemini 3.**
