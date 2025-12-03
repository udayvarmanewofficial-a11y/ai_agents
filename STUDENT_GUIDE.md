# Student Guide: Understanding the Multi-Agent Planner

This guide is designed specifically for students to understand how this application works, why certain design decisions were made, and how to use it effectively for their learning and planning needs.

## 🎯 What Problem Does This Solve?

As a student, you often need to:

- Plan study schedules for exams
- Break down large learning goals into manageable tasks
- Find the right resources and topics to study
- Get feedback on whether your plan is realistic

This application uses AI agents to help you create comprehensive, realistic plans by:

1. **Researching** what you need to learn (using your uploaded materials and AI knowledge)
2. **Planning** a detailed schedule with specific tasks and timelines
3. **Reviewing** the plan to ensure it's realistic and well-structured

## 🤖 How It Works: The Multi-Agent System

### Why Multiple Agents?

Think of this like having a study group with three specialized friends:

**Friend 1 - The Researcher** 📚

- Helps you gather information about the topic
- Reviews your uploaded study materials
- Identifies key concepts and resources
- **Example**: "For Python certification, you need to know: data structures, OOP, modules, file handling..."

**Friend 2 - The Planner** 📅

- Takes the research and creates a detailed study schedule
- Breaks down big topics into daily/weekly tasks
- Sets realistic timelines and milestones
- **Example**: "Week 1: Study data structures (lists, tuples). Practice 30 mins daily. Complete exercises 1-10."

**Friend 3 - The Reviewer** ✅

- Reviews the plan for issues or improvements
- Makes sure it's realistic and achievable
- Refines based on your feedback
- **Example**: "This plan looks good, but Week 3 seems too heavy. Let's spread it across two weeks."

### Why This is Better Than One Agent

Imagine asking one person to research, plan, AND review all at once. They might:

- Miss important details
- Create an unrealistic plan
- Not catch their own mistakes

By splitting the work, each agent focuses on doing one thing really well, leading to higher quality results.

## 📚 The Knowledge Base (RAG System)

### What is RAG?

RAG stands for "Retrieval-Augmented Generation." In simple terms:

- You upload your class notes, textbooks, or study materials
- The system "reads" and "remembers" these documents
- When planning, it refers to YOUR materials, not just generic information

### How It Works Under the Hood

1. **Document Upload**:

   ```
   You upload: "Python_Course_Notes.pdf"
   ↓
   System splits it into chunks (pieces of text)
   ↓
   Each chunk gets a "fingerprint" (embedding)
   ↓
   Stored in a database for quick retrieval
   ```

2. **When Creating a Plan**:
   ```
   Your request: "I need to prepare for Python exam"
   ↓
   System searches: "What do I know about Python?"
   ↓
   Finds relevant chunks from your uploaded notes
   ↓
   Includes this in the research phase
   ```

### Why This is Powerful

Without RAG:

- AI uses only its general knowledge
- Might miss specific topics YOUR course covers
- Generic advice that doesn't match your curriculum

With RAG:

- AI knows what YOUR professor teaches
- References YOUR textbook and notes
- Plan is customized to YOUR specific exam

### What Makes Good Upload Materials?

**Best Materials to Upload**:

- ✅ Course syllabus
- ✅ Lecture notes
- ✅ Textbook chapters
- ✅ Past exam papers
- ✅ Assignment guidelines

**Less Useful**:

- ❌ Random internet articles (AI already knows general info)
- ❌ Very short documents (not enough context)
- ❌ Images without text (can't be processed yet)

## 🔧 Technical Concepts Explained Simply

### Frontend (What You See)

The website you interact with is built with:

- **React**: A library that makes websites interactive and fast
- **TypeScript**: Adds safety to code (catches errors before they happen)
- **Tailwind CSS**: Makes everything look nice and consistent

**Analogy**: Think of it like building with LEGO blocks. React provides the blocks, TypeScript makes sure they fit together correctly, and Tailwind CSS paints them nicely.

### Backend (What Powers It)

The server that handles your requests uses:

- **FastAPI**: A modern, fast Python framework
- **PostgreSQL**: A database that stores your tasks and files
- **Qdrant**: A special database for searching your documents

**Analogy**: Like a restaurant kitchen. FastAPI is the head chef (coordinates everything), PostgreSQL is the inventory system (tracks orders), and Qdrant is the recipe book (quickly finds relevant recipes).

### LLM Providers (The AI Brain)

The system can use two AI providers:

- **OpenAI GPT-4**: Very smart, highest quality, more expensive
- **Google Gemini**: Smart, good quality, more affordable

**When to Use Which**:

- **GPT-4**: Important exams, complex topics, need best quality
- **Gemini**: Regular study planning, budget-conscious, still good results

### Vector Embeddings (How Documents are "Understood")

This is the most technical concept, but here's a simple explanation:

**Text → Numbers → Similarity**

1. "Python is a programming language" → [0.2, 0.5, 0.1, ...]
2. "Java is a programming language" → [0.2, 0.5, 0.09, ...]
3. "I like pizza" → [0.8, 0.1, 0.9, ...]

Notice how Python and Java have similar numbers (both about programming), but pizza is very different.

When you ask "What do I need to know about Python?", the system:

1. Converts your question to numbers
2. Finds document chunks with similar numbers
3. Those are the most relevant pieces to include

**Why This Works**: Similar meanings = similar numbers, making search fast and accurate.

## 💡 Best Practices for Students

### Creating Effective Planning Requests

**Bad Request**:

```
"Help me study"
```

Too vague! The AI doesn't know what to plan for.

**Good Request**:

```
Title: "Prepare for Calculus Midterm"
Description: "I have a calculus midterm in 3 weeks covering
limits, derivatives, and integrals. I can study 2 hours per
day on weekdays and 4 hours on weekends. I'm comfortable with
limits but struggling with integration techniques. I have my
class notes and the textbook already uploaded."
```

**Why This is Better**:

- Clear timeline (3 weeks)
- Specific topics (limits, derivatives, integrals)
- Your constraints (hours per day)
- Your current level (good at limits, weak at integration)
- Resources available (notes uploaded)

### Uploading Documents Strategically

**Strategy 1: Course Structure**

```
1. Upload syllabus first (AI learns course structure)
2. Upload lecture notes by week (covers what was taught)
3. Upload practice problems (AI sees question types)
```

**Strategy 2: Priority Materials**

```
1. Most important: Exam guidelines, sample tests
2. Core content: Textbook key chapters
3. Supplementary: Your notes, study guides
```

**Tip**: Name files clearly!

- ✅ `Week3_Derivatives_Notes.pdf`
- ❌ `notes.pdf`

### Modifying Plans

After getting a plan, you might want to change it:

**Good Modification Requests**:

- "Add more practice problems for integration"
- "I have a basketball game on Fridays, remove Friday study sessions"
- "Swap Week 2 and Week 3 because I learn this topic in class next week"

**Less Helpful**:

- "Make it better" (too vague)
- "Add everything" (unfocused)

## 🎓 Educational Value: Learning From the System

### Understanding Software Architecture

This project demonstrates several important concepts:

1. **Separation of Concerns**:

   - Frontend: Handles display
   - Backend: Handles logic
   - Database: Handles storage

   **Lesson**: Don't mix different responsibilities in one place.

2. **API Design**:

   - RESTful endpoints (`/api/v1/tasks/create`)
   - Clear request/response formats

   **Lesson**: Good APIs are predictable and well-documented.

3. **Async Programming**:

   - AI calls can take 10-30 seconds
   - System handles multiple requests simultaneously

   **Lesson**: Don't block waiting for slow operations.

4. **Data Modeling**:

   - Tasks have status (pending → processing → completed)
   - Files linked to their vector embeddings

   **Lesson**: Model real-world relationships in data structures.

### Learning About AI/ML

1. **Prompt Engineering**:
   Look at how agents have different system prompts in `backend/app/agents/`:

   - Researcher: "You are an expert Researcher Agent..."
   - Planner: "You are an expert Planner Agent..."

   **Lesson**: How you ask the AI matters enormously.

2. **RAG (Retrieval-Augmented Generation)**:

   - Not all AI needs to be trained from scratch
   - Can give AI access to specific information

   **Lesson**: Combine retrieval (search) with generation (AI creation).

3. **Vector Databases**:

   - Traditional DB: Exact match ("Find Python")
   - Vector DB: Semantic match ("Find programming languages")

   **Lesson**: Different data structures for different search needs.

### Understanding Production Systems

1. **Environment Configuration**:

   - Development: Easy debugging, verbose logging
   - Production: Optimized, secure

   **Lesson**: Code runs in different environments with different needs.

2. **Docker & Containers**:

   - Package everything needed to run the app
   - Works same on any computer

   **Lesson**: "Works on my machine" → "Works everywhere"

3. **Error Handling**:

   - What if API key is wrong?
   - What if file upload fails?
   - What if database is down?

   **Lesson**: Plan for failures, not just success.

## 🚀 Getting Started: Your First Task

### Step 1: Setup (One Time)

```bash
# Clone the repository
git clone https://github.com/varmakarthik12/planner-llm.git
cd planner-llm

# Run setup script
./setup.sh

# Add your API keys to .env file
```

### Step 2: Upload Study Materials

1. Go to "Knowledge Base" tab
2. Drag and drop your course materials
3. Wait for processing (you'll see "indexed" status)

### Step 3: Create Your First Plan

1. Go to "Planning" tab
2. Click "New Task"
3. Fill in your details (be specific!)
4. Wait 2-3 minutes for agents to work
5. Review the plan

### Step 4: Refine and Use

1. Click "Modify Plan" if needed
2. Export or copy the plan
3. Start following your schedule!

## ❓ Common Questions

**Q: How much does it cost to run?**
A: Main cost is API calls to OpenAI/Gemini. Estimate:

- $0.10-0.30 per task (GPT-4)
- $0.02-0.05 per task (Gemini)
- Infrastructure: Free (self-hosted)

**Q: Is my data private?**
A: Yes! Everything runs on your computer/server. Documents never leave your infrastructure (except when sending to LLM APIs for processing).

**Q: Can I use this offline?**
A: Partially. RAG and document storage work offline, but you need internet for LLM API calls (OpenAI/Gemini).

**Q: What if I don't have API keys?**
A: You need at least one (OpenAI or Gemini) to use the system. Both offer free trial credits.

**Q: How accurate are the plans?**
A: Very good for structured learning (exams, courses). Less accurate for creative or open-ended goals. Always review and adjust based on your situation.

## 🔍 Exploring the Code

Want to learn more? Here's where to look:

**Understanding Agents**:

```
backend/app/agents/
├── researcher_agent.py   ← How research works
├── planner_agent.py      ← How planning works
└── reviewer_agent.py     ← How review works
```

**Understanding RAG**:

```
backend/app/services/
├── rag/                  ← Main RAG logic
├── embeddings/           ← How text → numbers
├── vector_db/            ← How search works
└── document_processor/   ← How files are split
```

**Understanding Frontend**:

```
frontend/src/
├── pages/                ← What you see
├── services/             ← How it talks to backend
└── App.tsx               ← Main app component
```

## 📈 Taking It Further

Once you understand the basics:

1. **Experiment with Prompts**: Try changing agent system messages
2. **Add New Agents**: Create a "Budget Agent" or "Resource Finder Agent"
3. **Improve RAG**: Try different chunking strategies
4. **Add Features**: Email reminders, calendar integration, etc.
5. **Optimize Costs**: Cache frequent queries, use cheaper models for some tasks

## 🎯 Key Takeaways

1. **Multi-agent systems** produce better results than single agents
2. **RAG** makes AI work with your specific information
3. **Good architecture** separates concerns and scales well
4. **User experience** is about understanding user needs and workflows
5. **Production systems** require careful planning for errors, security, and scale

---

**Remember**: The best way to learn is by using and experimenting. Don't be afraid to break things (that's what learning is all about)! Start with simple tasks, upload some documents, and see how the system works.

Happy planning! 📚✨

---

**Need Help?**

- Check the [README.md](./README.md) for setup
- See [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
- Read [DECISIONS.md](./DECISIONS.md) for why things are built this way
- Open an issue on GitHub if stuck
