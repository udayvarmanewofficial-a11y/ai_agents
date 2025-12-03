# Architecture Documentation

## System Overview

The Multi-Agent Planning System is a full-stack web application that uses multiple specialized AI agents to create comprehensive plans and schedules. It integrates a RAG (Retrieval-Augmented Generation) system to leverage private knowledge bases.

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        User Interface                          │
│                    (React + TypeScript)                        │
└───────────────────────────┬────────────────────────────────────┘
                            │ HTTP/WebSocket
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Task API   │  │   RAG API    │  │  Health API  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└───────┬────────────────────┬───────────────────┬───────────────┘
        │                    │                   │
        ▼                    ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Agent         │    │  RAG         │    │  Database    │
│Orchestrator  │◄───│  Service     │    │  Services    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────┐
│              Infrastructure Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌────────┐  ┌──────┐ │
│  │PostgreSQL│  │  Qdrant  │  │ Redis  │  │ LLMs │ │
│  └──────────┘  └──────────┘  └────────┘  └──────┘ │
└─────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (React Application)

**Technology Stack**:

- React 18 with TypeScript
- Tailwind CSS for styling
- React Router for navigation
- Axios for API communication
- React Markdown for rendering agent outputs

**Key Components**:

```
frontend/src/
├── pages/
│   ├── PlannerPage.tsx      # Main planning interface
│   ├── TaskDetailPage.tsx   # Task details and results
│   └── RAGPage.tsx           # Knowledge base management
├── services/
│   ├── api.ts               # Axios configuration
│   ├── taskService.ts       # Task API calls
│   └── ragService.ts        # RAG API calls
└── App.tsx                   # Main application component
```

**Design Decisions**:

- **TypeScript**: Type safety reduces runtime errors
- **Tailwind**: Utility-first CSS for rapid UI development
- **Component-based**: Reusable, maintainable code structure
- **Service layer**: Separated API logic from UI components

### 2. Backend (FastAPI Application)

**Technology Stack**:

- FastAPI for REST API
- SQLAlchemy for database ORM
- Pydantic for data validation
- asyncio for concurrent operations

**Folder Structure**:

```
backend/app/
├── api/
│   └── v1/
│       ├── tasks.py          # Task endpoints
│       └── rag.py            # RAG endpoints
├── agents/
│   ├── base_agent.py         # Base agent class
│   ├── researcher_agent.py   # Research specialist
│   ├── planner_agent.py      # Planning specialist
│   ├── reviewer_agent.py     # Review specialist
│   └── orchestrator.py       # Agent coordinator
├── services/
│   ├── llm/                  # LLM provider abstraction
│   │   ├── base_provider.py
│   │   ├── openai_provider.py
│   │   └── gemini_provider.py
│   ├── rag/                  # RAG service
│   ├── embeddings/           # Embedding generation
│   ├── vector_db/            # Vector database client
│   └── document_processor/   # Document parsing & chunking
├── models/                   # SQLAlchemy models
├── schemas/                  # Pydantic schemas
├── core/                     # Configuration & logging
├── db/                       # Database session management
└── main.py                   # Application entry point
```

**Design Decisions**:

- **Modular architecture**: Each service is self-contained
- **Dependency injection**: FastAPI's dependency system for clean code
- **Async/await**: Non-blocking operations for better performance
- **Type hints**: Python type hints throughout for clarity

### 3. Multi-Agent System

The system uses three specialized agents that work in sequence:

#### Agent Workflow

```
┌─────────────────┐
│  User Request   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      Researcher Agent               │
│  • Queries RAG knowledge base       │
│  • Analyzes task requirements       │
│  • Identifies key topics            │
│  • Provides research findings       │
└────────┬────────────────────────────┘
         │ Research Output
         ▼
┌─────────────────────────────────────┐
│      Planner Agent                  │
│  • Reviews research findings        │
│  • Creates structured plan          │
│  • Defines timeline & milestones    │
│  • Breaks down into tasks           │
└────────┬────────────────────────────┘
         │ Plan Output
         ▼
┌─────────────────────────────────────┐
│      Reviewer Agent                 │
│  • Reviews the plan                 │
│  • Identifies improvements          │
│  • Refines and optimizes            │
│  • Produces final output            │
└────────┬────────────────────────────┘
         │ Final Output
         ▼
┌─────────────────┐
│  User Receives  │
│   Final Plan    │
└─────────────────┘
```

#### Agent Base Class

All agents inherit from `BaseAgent` which provides:

- LLM provider access (OpenAI or Gemini)
- RAG query capabilities
- Standardized output formatting
- Error handling and logging

#### Agent Orchestrator

The orchestrator manages the workflow:

```python
1. Initialize all three agents
2. Execute Researcher Agent → get research output
3. Pass research to Planner Agent → get plan output
4. Pass both to Reviewer Agent → get final output
5. Store results in database
6. Send progress updates via callback
```

### 4. RAG (Retrieval-Augmented Generation) System

#### Components

```
Document Upload
      │
      ▼
┌──────────────────┐
│  File Validation │  (size, type checks)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│Document Processor│  (extract text: PDF, DOCX, etc.)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Text Chunker   │  (recursive character splitting)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│Embedding Service │  (sentence-transformers)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Vector Store    │  (Qdrant)
│  (with metadata) │
└──────────────────┘
```

#### Chunking Strategy

**Why This Approach**:

- **Recursive splitting**: Preserves semantic boundaries (paragraphs → sentences → words)
- **Overlap**: Ensures context isn't lost at chunk boundaries
- **Size optimization**: Balances retrieval precision vs. context coverage

```python
Chunk Size: 1000 characters
Overlap: 200 characters

Example:
Original text: [============================================]
Chunk 1:      [=========>   ]
Chunk 2:              [<===]=========>   ]
Chunk 3:                          [<===]========>]
```

#### Vector Database (Qdrant)

**Why Qdrant**:

- **Performance**: Fast similarity search with HNSW algorithm
- **Filtering**: Metadata filtering (e.g., by user_id)
- **Scalability**: Handles millions of vectors efficiently
- **Self-hosted**: Full control over data

**Alternative Considered**: ChromaDB (lighter but less feature-rich), Pinecone (managed but requires external service)

### 5. LLM Provider Abstraction

**Design Pattern**: Strategy Pattern

```
┌──────────────────────┐
│  BaseLLMProvider     │  (Abstract interface)
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼────┐  ┌────▼─────┐
│OpenAI  │  │  Gemini  │
│Provider│  │  Provider│
└────────┘  └──────────┘
```

**Benefits**:

- Easy to add new providers (e.g., Anthropic Claude)
- Consistent interface across different LLMs
- Centralized error handling and retry logic
- Provider-specific optimizations

**Factory Pattern**: `LLMProviderFactory` creates appropriate provider instance based on configuration

### 6. Database Architecture

#### PostgreSQL Schema

```sql
-- Tasks table
CREATE TABLE tasks (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    task_type VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    llm_provider VARCHAR NOT NULL,
    model_name VARCHAR,
    research_output JSON,
    plan_output JSON,
    review_output JSON,
    final_output JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Agent execution logs
CREATE TABLE agent_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR REFERENCES tasks(id),
    agent_type VARCHAR NOT NULL,
    input_data JSON NOT NULL,
    output_data JSON,
    status VARCHAR NOT NULL,
    error_message TEXT,
    execution_time_seconds FLOAT,
    tokens_used INTEGER,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Uploaded files metadata
CREATE TABLE uploaded_files (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    filename VARCHAR NOT NULL,
    original_filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    file_type VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'uploaded',
    chunks_count INTEGER DEFAULT 0,
    vector_ids JSON,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);
```

**Why PostgreSQL**:

- Mature, reliable relational database
- Excellent JSON support for flexible schemas
- ACID compliance for data integrity
- Good performance for metadata queries

#### Qdrant Collections

```
Collection: knowledge_base
├── Vector dimension: 384 (from all-MiniLM-L6-v2)
├── Distance metric: Cosine similarity
└── Payload schema:
    ├── text: String (chunk content)
    ├── file_id: String
    ├── user_id: String
    ├── filename: String
    ├── chunk_index: Integer
    └── chunk_size: Integer
```

#### Redis

**Usage**:

- **Caching**: LLM responses, RAG search results
- **Job Queue**: Background task processing
- **Rate Limiting**: API request throttling

### 7. Security Considerations

**Current Implementation**:

- Environment-based secrets (API keys, passwords)
- CORS configuration for cross-origin requests
- Input validation with Pydantic
- SQL injection prevention via SQLAlchemy ORM

**Production Recommendations**:

- Add JWT-based authentication
- Implement rate limiting per user
- Add API key authentication
- Enable HTTPS/TLS
- Implement user isolation in vector DB (metadata filtering)
- Add request logging and audit trails

### 8. Scalability Considerations

**Current Design**:

- Stateless API (horizontal scaling possible)
- Background task processing
- Database connection pooling
- Async/await for I/O operations

**Scaling Strategies**:

1. **Horizontal Scaling**:

   ```
   Load Balancer
        │
        ├─── Backend Instance 1
        ├─── Backend Instance 2
        └─── Backend Instance 3
   ```

2. **Database Optimization**:

   - Read replicas for PostgreSQL
   - Qdrant clustering for large-scale vector search
   - Redis cluster for caching

3. **Queueing System**:

   - Replace background tasks with Celery + RabbitMQ
   - Dedicated worker processes for agent execution

4. **Caching Strategy**:
   - Cache frequent RAG queries
   - Cache LLM responses (with TTL)
   - CDN for frontend static assets

### 9. Monitoring and Observability

**Recommended Tools**:

- **Logging**: Structured JSON logs via Loguru
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry for distributed tracing
- **Alerting**: Alert on task failures, high latency, API errors

**Key Metrics to Track**:

- Agent execution time per type
- LLM token usage and costs
- RAG search latency
- File processing time
- API request rate and errors

### 10. Cost Optimization

**Token Usage Management**:

```python
# Track tokens per request
def track_usage(response):
    tokens = response['tokens_used']
    cost = calculate_cost(tokens, model_name)
    log_to_metrics(cost)
    return tokens
```

**Strategies**:

- Use GPT-3.5-turbo for research (cheaper)
- Use GPT-4 only for planning and review
- Cache identical queries
- Implement token limits per user
- Use local embeddings (sentence-transformers) instead of OpenAI embeddings

## Data Flow Diagrams

### Task Creation Flow

```
User Submit Task
      │
      ▼
API Validation (Pydantic)
      │
      ▼
Create Task Record (PostgreSQL)
      │
      ▼
Background Task Spawned
      │
      ├─────────────────────────────────────┐
      │                                     │
      ▼                                     ▼
Researcher Agent                    Update Task Status
      │                                     │
      ├─► Query RAG                        │
      ├─► Generate Research                 │
      ├─► Store Research Output ───────────┘
      │
      ▼
Planner Agent
      │
      ├─► Use Research Output
      ├─► Generate Plan
      ├─► Store Plan Output
      │
      ▼
Reviewer Agent
      │
      ├─► Review Research + Plan
      ├─► Generate Final Output
      ├─► Store Final Output
      │
      ▼
Update Task (Status = Completed)
      │
      ▼
User Receives Notification
```

### RAG Query Flow

```
User Query
    │
    ▼
Generate Query Embedding (Sentence Transformer)
    │
    ▼
Search Qdrant Vector DB
    │
    ├─► Apply filters (user_id)
    ├─► Similarity search (cosine)
    └─► Get top-k results
    │
    ▼
Format Results
    │
    ├─► Extract text chunks
    ├─► Add metadata
    └─► Score results
    │
    ▼
Return to Agent/User
    │
    ▼
Agent Uses Context in LLM Prompt
```

## Technology Choices & Rationale

### Why FastAPI?

- **Modern**: Built on modern Python (3.7+) with type hints
- **Fast**: High performance, comparable to Node.js
- **Async**: Native async/await support
- **Documentation**: Auto-generated OpenAPI docs
- **Validation**: Built-in request/response validation

### Why React?

- **Component-based**: Reusable UI components
- **Ecosystem**: Vast library ecosystem
- **Performance**: Virtual DOM for efficient updates
- **TypeScript**: Type safety in frontend

### Why Qdrant?

- **Purpose-built**: Designed specifically for vector search
- **Performance**: Highly optimized for similarity search
- **Features**: Rich filtering, batch operations
- **Self-hosted**: Full data control, no external dependencies

### Why Sentence Transformers?

- **Quality**: High-quality embeddings
- **Speed**: Fast local inference
- **Cost**: No API costs
- **Privacy**: Data stays local

## Future Enhancements

1. **Authentication & Authorization**:

   - User registration and login
   - JWT-based API authentication
   - Role-based access control

2. **Advanced Features**:

   - WebSocket for real-time updates
   - Plan templates and presets
   - Collaboration features (share plans)
   - Export plans (PDF, DOCX, Calendar)

3. **Agent Improvements**:

   - Specialized agents (e.g., Budget Agent, Timeline Agent)
   - Agent memory and learning
   - Multi-turn conversations
   - Agent tool use (web search, calculator, etc.)

4. **RAG Enhancements**:

   - Semantic chunking (context-aware splitting)
   - Multi-modal support (images, videos)
   - Hybrid search (keyword + semantic)
   - Query rewriting and expansion

5. **DevOps**:
   - Kubernetes deployment
   - CI/CD pipelines
   - Automated testing
   - Performance monitoring

---

This architecture is designed to be modular, scalable, and maintainable, following software engineering best practices while being optimized for the specific use case of multi-agent planning with RAG capabilities.
