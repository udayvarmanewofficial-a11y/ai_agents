# Design Decisions and Rationale

This document explains the major technical and architectural decisions made in building the Multi-Agent Planning System. Understanding these decisions will help developers and users appreciate the design trade-offs and implementation choices.

## Table of Contents

1. [Technology Stack Decisions](#technology-stack-decisions)
2. [Architecture Decisions](#architecture-decisions)
3. [Multi-Agent System Design](#multi-agent-system-design)
4. [RAG System Decisions](#rag-system-decisions)
5. [Database Choices](#database-choices)
6. [Security & Performance](#security--performance)
7. [UI/UX Decisions](#uiux-decisions)
8. [Trade-offs & Alternatives](#trade-offs--alternatives)

---

## Technology Stack Decisions

### Backend: FastAPI

**Decision**: Use FastAPI instead of Flask, Django, or other Python frameworks.

**Rationale**:

1. **Performance**: FastAPI is one of the fastest Python frameworks, rivaling Node.js in speed
2. **Modern Python**: Built on Python 3.7+ type hints, leveraging the latest language features
3. **Async Support**: Native async/await support crucial for handling multiple LLM calls
4. **Auto Documentation**: Automatic OpenAPI/Swagger documentation generation
5. **Data Validation**: Built-in Pydantic validation reduces boilerplate code
6. **WebSocket Support**: Native support for real-time features (future enhancement)

**Alternatives Considered**:

- **Flask**: Lightweight but lacks built-in async and validation
- **Django**: Feature-rich but too heavyweight for our API-focused needs
- **Node.js/Express**: Great performance but team expertise in Python

**Outcome**: FastAPI provides the perfect balance of performance, modern features, and developer experience.

---

### Frontend: React with TypeScript

**Decision**: Use React with TypeScript instead of Vue, Angular, or plain JavaScript.

**Rationale**:

1. **Component Reusability**: React's component-based architecture fits our needs
2. **Type Safety**: TypeScript catches errors at compile-time, reducing bugs
3. **Ecosystem**: Largest ecosystem of libraries and tools
4. **Developer Experience**: Excellent tooling, debugging, and community support
5. **Performance**: Virtual DOM provides efficient UI updates
6. **Learning Curve**: Well-documented, easier for team members to learn

**Why TypeScript over JavaScript**:

- Type safety for API contracts (matching backend schemas)
- Better IDE support (autocomplete, refactoring)
- Self-documenting code through types
- Catches common errors before runtime

**Alternatives Considered**:

- **Vue.js**: Simpler learning curve but smaller ecosystem
- **Angular**: Full-featured but steeper learning curve and more opinionated
- **Svelte**: Excellent performance but smaller community

**Outcome**: React + TypeScript provides the best balance of productivity, maintainability, and type safety.

---

### Styling: Tailwind CSS

**Decision**: Use Tailwind CSS instead of traditional CSS, CSS Modules, or component libraries.

**Rationale**:

1. **Utility-First**: Rapid development without context switching
2. **Consistency**: Design system baked into utility classes
3. **Bundle Size**: PurgeCSS removes unused styles in production
4. **Customization**: Easily customize via configuration
5. **Responsive**: Mobile-first responsive design built-in
6. **No Naming Conflicts**: No need to invent class names

**Alternatives Considered**:

- **Material-UI/Ant Design**: Too opinionated, harder to customize
- **Bootstrap**: Older paradigm, less flexible
- **Styled Components**: Runtime overhead, no build-time optimization

**Outcome**: Tailwind enables rapid UI development while maintaining consistency and performance.

---

## Architecture Decisions

### Microservices vs Monolith

**Decision**: Use a modular monolith (single backend, single frontend).

**Rationale**:

1. **Simplicity**: Easier to develop, test, and deploy
2. **Shared Code**: Services can easily share utilities and models
3. **Atomic Deployments**: Single deployment unit, no version skew
4. **Transaction Management**: Easier to maintain data consistency
5. **Team Size**: Small team doesn't justify microservices overhead
6. **Refactoring**: Can extract services later if needed

**When to Consider Microservices**:

- Team grows beyond 10-15 developers
- Different services need different scaling characteristics
- Independent deployment cycles required
- Different technology stacks per service

**Outcome**: Modular monolith provides simplicity while maintaining clean boundaries between components.

---

### Asynchronous Architecture

**Decision**: Use async/await throughout the backend for I/O operations.

**Rationale**:

1. **LLM Latency**: LLM API calls can take 5-30 seconds
2. **Concurrent Requests**: Handle multiple user requests efficiently
3. **Database I/O**: Non-blocking database queries
4. **File Processing**: Concurrent document processing
5. **Scalability**: Better resource utilization per server

**Implementation**:

```python
# Sequential (bad - blocks thread)
research = researcher.execute()
plan = planner.execute()
review = reviewer.execute()

# Async (good - non-blocking)
research = await researcher.execute()
plan = await planner.execute()
review = await reviewer.execute()
```

**Trade-off**: Slightly more complex code, but significant performance gains.

**Outcome**: Async architecture enables efficient handling of long-running LLM operations.

---

## Multi-Agent System Design

### Why Three Agents?

**Decision**: Use three specialized agents (Researcher, Planner, Reviewer) instead of a single agent.

**Rationale**:

1. **Separation of Concerns**: Each agent has a clear, focused responsibility
2. **Quality**: Specialized agents produce better results than generalists
3. **Modularity**: Easy to improve or replace individual agents
4. **Transparency**: Users can see each agent's contribution
5. **Iterative Refinement**: Multiple passes improve output quality
6. **Token Efficiency**: Each agent can use appropriate model size/cost

**Agent Specialization**:

**Researcher Agent**:

- **Why**: Information gathering requires different skills than planning
- **Unique**: Queries RAG system, synthesizes information
- **Output**: Research findings, relevant context

**Planner Agent**:

- **Why**: Creating structured plans requires specific expertise
- **Unique**: Timeline creation, task breakdown, resource allocation
- **Output**: Detailed, actionable plan with milestones

**Reviewer Agent**:

- **Why**: Quality assurance and refinement needs critical thinking
- **Unique**: Identifies gaps, suggests improvements, handles modifications
- **Output**: Refined plan with feedback incorporated

**Alternative Considered**: Single agent with long prompt

- Pros: Simpler architecture, fewer API calls
- Cons: Lower quality, less transparent, harder to debug

**Outcome**: Three-agent system produces higher quality plans with better transparency.

---

### Sequential vs Parallel Execution

**Decision**: Execute agents sequentially (Research → Plan → Review).

**Rationale**:

1. **Dependencies**: Each agent needs previous agent's output
2. **Context Building**: Sequential flow allows context accumulation
3. **Quality**: Each stage refines and improves upon the previous
4. **Predictability**: Deterministic order makes debugging easier

**When Parallel Execution Makes Sense**:

- Independent research queries
- Multiple document processing
- Generating variations of a plan

**Outcome**: Sequential execution provides best quality while parallel sub-tasks optimize performance.

---

### Agent Base Class Design

**Decision**: Create abstract base class that all agents inherit from.

**Rationale**:

1. **Code Reuse**: Common functionality in one place
2. **Consistency**: All agents follow same interface
3. **Extensibility**: Easy to add new agents
4. **Testing**: Can mock base class methods
5. **Type Safety**: Type hints for agent contracts

**Base Class Responsibilities**:

```python
class BaseAgent(ABC):
    - LLM provider management
    - RAG query interface
    - Standard output formatting
    - Error handling & logging
    - execute() abstract method
```

**Benefits**:

- New agent creation requires only implementing `execute()`
- Shared RAG access logic
- Consistent error handling

**Outcome**: Base class reduces code duplication and ensures consistency across agents.

---

## RAG System Decisions

### Vector Database: Qdrant

**Decision**: Use Qdrant for vector storage instead of alternatives.

**Rationale**:

1. **Performance**: Optimized for similarity search with HNSW algorithm
2. **Filtering**: Rich metadata filtering (crucial for multi-user)
3. **Scalability**: Handles millions of vectors efficiently
4. **Self-Hosted**: Full control over data, no vendor lock-in
5. **Features**: Batch operations, snapshots, cluster support
6. **Docker-Friendly**: Easy to deploy and manage

**Comparison with Alternatives**:

| Feature     | Qdrant | Pinecone | ChromaDB | Weaviate |
| ----------- | ------ | -------- | -------- | -------- |
| Self-hosted | ✅     | ❌       | ✅       | ✅       |
| Filtering   | ✅✅   | ✅       | ⚠️       | ✅       |
| Performance | ✅✅   | ✅✅     | ⚠️       | ✅       |
| Ease of use | ✅✅   | ✅✅     | ✅✅     | ⚠️       |
| Cost        | Free   | Paid     | Free     | Free     |
| Scalability | ✅✅   | ✅✅     | ⚠️       | ✅       |

**Why Not Pinecone**:

- Managed service costs scale with usage
- Data leaves your infrastructure
- Less control over performance tuning

**Why Not ChromaDB**:

- Newer, less battle-tested
- Limited filtering capabilities
- Smaller community

**Outcome**: Qdrant provides best balance of performance, features, and control.

---

### Embedding Model: Sentence-Transformers

**Decision**: Use local sentence-transformers (all-MiniLM-L6-v2) instead of OpenAI embeddings.

**Rationale**:

1. **Cost**: Zero per-request cost (only compute)
2. **Speed**: Local inference faster than API calls
3. **Privacy**: Documents never leave your infrastructure
4. **Reliability**: No external API dependencies
5. **Offline**: Works without internet connection

**Model Selection: all-MiniLM-L6-v2**:

- **Small**: Only 80MB model size
- **Fast**: Quick inference on CPU
- **Quality**: Excellent for general text (384 dimensions)
- **Popular**: Well-tested, widely used

**When to Use OpenAI Embeddings**:

- Need highest quality embeddings
- Infrastructure cost > API cost
- Don't want to manage model deployment

**Trade-offs**:

- Local: Faster, cheaper, but requires compute resources
- OpenAI: Higher quality, but costs scale with usage

**Outcome**: Local embeddings provide best balance for most use cases.

---

### Chunking Strategy: Recursive Character Splitting

**Decision**: Use recursive character splitting with overlap instead of fixed-size or semantic chunking.

**Rationale**:

1. **Semantic Preservation**: Splits at natural boundaries (paragraphs, sentences)
2. **Context Preservation**: Overlap ensures no information loss at boundaries
3. **Flexibility**: Works well across different document types
4. **Performance**: Fast processing without ML models
5. **Predictability**: Consistent chunk sizes for embedding

**Chunking Parameters**:

```python
CHUNK_SIZE = 1000 characters
CHUNK_OVERLAP = 200 characters
```

**Why These Values**:

- **1000 chars**: Fits in context window without being too small
- **200 chars overlap**: Enough context, not too much redundancy
- Balance between retrieval precision and coverage

**Splitting Hierarchy**:

1. Try paragraph breaks (`\n\n`)
2. Try line breaks (`\n`)
3. Try sentence breaks (`. `)
4. Try clause breaks (`, `)
5. Fall back to character split

**Alternatives Considered**:

- **Fixed-size**: Simple but breaks semantic boundaries
- **Semantic chunking** (using ML): Better quality but slower and more complex
- **Sentence-based**: Too small, loses context

**Outcome**: Recursive splitting provides best balance of quality, speed, and simplicity.

---

### File Upload Strategy

**Decision**: Synchronous upload with asynchronous processing.

**Rationale**:

1. **User Feedback**: Immediate confirmation of upload success
2. **Error Handling**: Catch file issues before processing
3. **Resource Management**: Process when resources available
4. **Progress Tracking**: Can show processing status
5. **Retry Logic**: Failed processing can be retried

**Flow**:

```
Upload → Validate → Save File → Return Success → Background: Process & Index
```

**For Large Files**:

- Stream upload to disk (avoids memory issues)
- Process in chunks (prevents timeout)
- Store progress in database

**Alternatives Considered**:

- **Fully synchronous**: Simple but blocks user, can timeout
- **Chunked upload**: Complex client-side logic
- **Direct streaming to processing**: No recovery on failure

**Outcome**: Hybrid approach provides best user experience with reliable processing.

---

## Database Choices

### Primary Database: PostgreSQL

**Decision**: Use PostgreSQL instead of MySQL, MongoDB, or other databases.

**Rationale**:

1. **Relational Model**: Task relationships naturally relational
2. **JSON Support**: Excellent JSONB for flexible agent outputs
3. **ACID Compliance**: Ensures data integrity
4. **Performance**: Fast queries with proper indexes
5. **Mature**: Decades of production use, extensive tooling
6. **Extensions**: PostGIS, full-text search if needed

**Data That Benefits from Relational Model**:

- Task metadata and relationships
- User sessions and permissions
- Agent execution logs
- File metadata

**Data That Benefits from JSON**:

- Agent outputs (varying structure)
- Task configuration (flexible fields)
- Metadata payloads

**Why Not MongoDB**:

- Our queries are relational (joins, constraints)
- Don't need MongoDB's horizontal scaling (yet)
- Stronger guarantees with ACID transactions

**Outcome**: PostgreSQL provides best of both worlds (relational + JSON).

---

### Caching Layer: Redis

**Decision**: Use Redis for caching and future job queue.

**Rationale**:

1. **Speed**: In-memory, microsecond latency
2. **Simplicity**: Simple key-value model
3. **Durability**: Optional persistence
4. **Versatility**: Cache, queue, pub/sub
5. **Mature**: Battle-tested at scale

**Use Cases**:

- **Cache LLM responses** (same prompt = cached result)
- **Cache RAG queries** (popular searches)
- **Rate limiting** (API throttling)
- **Session storage** (future auth)
- **Job queue** (future: Celery backend)

**Alternatives Considered**:

- **Memcached**: Faster but less features
- **No cache**: Simpler but slower, more expensive

**Outcome**: Redis provides essential caching with room for growth.

---

## Security & Performance

### Authentication Strategy

**Current**: Simple user_id parameter (development mode)

**Future**: JWT-based authentication

**Rationale for JWT**:

1. **Stateless**: No server-side session storage
2. **Scalable**: Works across multiple servers
3. **Standard**: Well-understood, many libraries
4. **Flexible**: Can include claims (roles, permissions)

**Implementation Plan**:

```python
# Login endpoint returns JWT
POST /api/v1/auth/login
→ {"access_token": "eyJ...", "token_type": "bearer"}

# Protected endpoints verify JWT
Authorization: Bearer eyJ...
```

**Why Not Sessions**:

- Requires shared session store (Redis)
- Not stateless
- Harder to scale horizontally

**Outcome**: JWT planned for production, simple user_id for development.

---

### Rate Limiting

**Decision**: Implement rate limiting per user and globally.

**Rationale**:

1. **Cost Control**: LLM APIs charge per token
2. **Fair Usage**: Prevent single user from monopolizing resources
3. **DDoS Protection**: Guard against abuse
4. **Resource Management**: Prevent database overload

**Implementation Strategy**:

```python
# Per user: 10 tasks per hour
# Global: 100 tasks per hour
# LLM calls: 50 per user per hour
```

**Using Redis**:

```python
key = f"rate_limit:{user_id}:{endpoint}"
count = redis.incr(key)
redis.expire(key, 3600)  # 1 hour
if count > limit:
    raise RateLimitExceeded()
```

**Outcome**: Rate limiting protects resources while allowing fair use.

---

### Input Validation

**Decision**: Use Pydantic for all request validation.

**Rationale**:

1. **Type Safety**: Automatic type checking and conversion
2. **Validation**: Built-in validators (min, max, regex, etc.)
3. **Documentation**: Auto-generates schema for OpenAPI
4. **Error Messages**: Clear, actionable error messages
5. **Performance**: Fast validation using Rust (v2)

**Example**:

```python
class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    task_type: TaskType  # Enum validation

    @validator('title')
    def validate_title(cls, v):
        if '<script>' in v.lower():
            raise ValueError('Invalid characters')
        return v
```

**Benefits**:

- Prevents SQL injection (via ORM)
- Prevents XSS (via validation)
- Ensures data integrity
- Documents API contracts

**Outcome**: Pydantic provides comprehensive validation with minimal code.

---

## UI/UX Decisions

### Single Page Application

**Decision**: Build as SPA instead of server-side rendered app.

**Rationale**:

1. **Interactivity**: Rich client-side interactions
2. **Performance**: Fast navigation, no full page reloads
3. **Separation**: Clear API boundary between frontend/backend
4. **Modern UX**: Smooth, app-like experience
5. **Deployment**: Frontend and backend deploy independently

**Trade-offs**:

- **SEO**: Not critical for authenticated app
- **Initial Load**: Slightly slower first load (but cached)
- **JavaScript Required**: Acceptable for target audience

**Outcome**: SPA provides best user experience for interactive planning tool.

---

### Real-time Updates

**Current**: Polling for task status updates (3-second interval)

**Future**: WebSocket for real-time updates

**Rationale for Polling (Current)**:

1. **Simplicity**: Easy to implement and debug
2. **Reliability**: HTTP is universal, no firewall issues
3. **Good Enough**: 3-second delay acceptable for our use case

**When to Use WebSocket**:

- Need sub-second latency
- Push notifications from server
- Bidirectional communication
- Many concurrent users

**Implementation Comparison**:

```javascript
// Polling (current)
const checkStatus = async () => {
  const status = await fetch(`/api/tasks/${id}`);
  if (status !== "completed") {
    setTimeout(checkStatus, 3000);
  }
};

// WebSocket (future)
const ws = new WebSocket("/ws/tasks/${id}");
ws.onmessage = (event) => {
  updateUI(JSON.parse(event.data));
};
```

**Outcome**: Polling is simpler and sufficient; WebSocket available as enhancement.

---

### Markdown for Output

**Decision**: Use Markdown for agent outputs instead of plain text or HTML.

**Rationale**:

1. **Formatting**: Rich formatting (headings, lists, emphasis)
2. **Safety**: Safer than raw HTML (no XSS)
3. **Portability**: Easy to export, copy, or convert
4. **Readability**: Human-readable in raw form
5. **LLM-Friendly**: LLMs generate Markdown naturally

**Rendering**:

```typescript
<ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
```

**Features Supported**:

- Headings, lists, emphasis
- Code blocks
- Tables (via remark-gfm)
- Links

**Alternative Considered**: Rich text editor (too complex for output display)

**Outcome**: Markdown provides perfect balance of formatting and simplicity.

---

## Trade-offs & Alternatives

### Cost vs Quality (LLM Selection)

**Decision**: Let users choose between providers and models.

**Trade-off Matrix**:

| Model       | Cost (1M tokens) | Quality    | Speed      |
| ----------- | ---------------- | ---------- | ---------- |
| GPT-4 Turbo | $10-30           | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     |
| GPT-3.5     | $0.50-1.50       | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ |
| Gemini Pro  | $0.50-1.50       | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   |

**Recommendation**:

- **Default**: GPT-4 Turbo for best quality
- **Budget**: GPT-3.5 for cost-sensitive users
- **Balance**: Gemini Pro for good quality at lower cost

**Outcome**: User choice provides flexibility based on needs.

---

### Self-Hosted vs Managed Services

**Decision**: Self-host all infrastructure (PostgreSQL, Qdrant, Redis).

**Rationale**:

1. **Cost**: Managed services expensive at scale
2. **Control**: Full control over configuration and optimization
3. **Privacy**: Data stays within infrastructure
4. **Learning**: Team learns infrastructure management
5. **Flexibility**: Can optimize for specific workloads

**When Managed Makes Sense**:

- Small team, no DevOps expertise
- Need enterprise SLAs
- Focus on features, not infrastructure
- Unpredictable scaling needs

**Managed Service Comparison**:

- **AWS RDS** vs Self-hosted PostgreSQL: 3-5x cost difference
- **Pinecone** vs Self-hosted Qdrant: Pay per usage vs fixed cost
- **Redis Cloud** vs Self-hosted: 2-4x cost difference

**Outcome**: Self-hosting provides best long-term value with acceptable operational overhead.

---

### Monorepo vs Polyrepo

**Decision**: Single repository with backend/ and frontend/ folders.

**Rationale**:

1. **Simplicity**: One repo to clone, one CI/CD pipeline
2. **Atomic Changes**: Update frontend and backend together
3. **Shared Documentation**: ARCHITECTURE.md covers full stack
4. **Versioning**: Single version number for the system
5. **Code Sharing**: Could share TypeScript types in future

**When Polyrepo Makes Sense**:

- Multiple independent services
- Different teams own different repos
- Different release cycles
- Want independent versioning

**Outcome**: Monorepo simplifies development without significant downsides.

---

## Lessons Learned & Best Practices

### 1. Start with Modular Monolith

Don't jump to microservices. A well-structured monolith with clear module boundaries provides 90% of the benefits with 10% of the complexity.

### 2. Invest in Type Safety

TypeScript in frontend and type hints in backend catch bugs early and serve as living documentation.

### 3. Use Standards

FastAPI's OpenAPI, Pydantic models, REST conventions—standards reduce cognitive load and improve interoperability.

### 4. Document Decisions

This document! Future developers (including future you) need to understand the "why" not just the "what".

### 5. Make It Work, Then Make It Better

We chose simpler solutions (polling instead of WebSocket, local embeddings instead of paid API) that work well enough. Optimize when needed, not preemptively.

### 6. Consider the User

Every technical decision should ultimately serve user needs. Multi-agent system provides better results despite complexity. RAG allows private knowledge. These improve user outcomes.

---

## Conclusion

These decisions were made with careful consideration of:

- **User needs**: Students need high-quality, customizable plans
- **Developer experience**: Clean code, good tools, clear patterns
- **Operational requirements**: Reliability, cost, performance
- **Future flexibility**: Easy to enhance and scale

Not every decision will be perfect for every use case, but each was made with clear rationale and understanding of trade-offs. As the system evolves, some decisions may change—that's okay! The important thing is to understand why decisions were made so future changes are informed.

---

**Last Updated**: November 2025

**Contributors**: System Architecture Team

**Questions?** See [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details or [README.md](./README.md) for usage guide.
