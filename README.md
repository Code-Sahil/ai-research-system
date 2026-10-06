# AI Research System

An evidence-grounded AI research pipeline that uses a local Large Language Model (LLM) to plan research, retrieve sources, evaluate evidence, extract claims, filter weak evidence, and synthesize a structured research report.

The system is designed as a modular research workflow rather than a simple chatbot. Each stage produces a structured artifact that becomes the input to the next stage.

---

## Overview

Given a broad research question, the system breaks the problem into smaller questions, searches for relevant sources, retrieves the actual source content, evaluates the sources, extracts evidence, filters unreliable evidence, and finally generates a research report.

### Pipeline

```text
Research Question
        │
        ▼
   ┌──────────┐
   │ Planner  │
   └────┬─────┘
        │
        ▼
 Subquestions
        │
        ▼
┌──────────────────┐
│ Query Generation │
└────────┬─────────┘
         │
         ▼
    Search Queries
         │
         ▼
   ┌───────────┐
   │ Retriever │
   └─────┬─────┘
         │
         ▼
 Candidate Sources
         │
         ▼
┌───────────────────┐
│ Source Fetcher    │
└─────────┬─────────┘
          │
          ▼
     Source Text
          │
          ▼
     ┌─────────┐
     │ Chunker │
     └────┬────┘
          │
          ▼
     Source Chunks
          │
          ▼
 ┌──────────────────┐
 │ Source Evaluator │
 └────────┬─────────┘
          │
          ▼
   Evaluated Sources
          │
          ▼
 ┌──────────────────┐
 │ Evidence         │
 │ Extractor        │
 └────────┬─────────┘
          │
          ▼
      Evidence
          │
          ▼
 ┌──────────────────┐
 │ Evidence Filter  │
 └────────┬─────────┘
          │
          ▼
  Filtered Evidence
          │
          ▼
 ┌──────────────────┐
 │    Synthesizer   │
 └────────┬─────────┘
          │
          ▼
    Research Report 

Key Features
- Local LLM inference using Ollama and Qwen
- Automatic research-question decomposition
- Search-query generation
- Web-source retrieval
- Source-quality and relevance evaluation
- Actual source-content extraction rather than relying only on search snippets
- Text chunking for downstream processing
- Evidence and claim extraction
- Evidence filtering
- Evidence-grounded report synthesis
- Confidence scoring
- Source traceability
- Modular pipeline architecture
- Intermediate JSON artifacts for reproducibility and debugging
- No paid LLM API required

Technology Stack
Component	     Technology
Language	     Python
LLM Runtime	     Ollama
Local Model	     Qwen3 8B
Web Retrieval	 ddgs
Environment	     Python virtual environment
Version Control	 Git / GitHub
Development	     VS Code
Output	         JSON / Markdown


Project Structure
ai-research-system/
│
├── .venv/
│
├── experiments/
│   └── questions.txt
│
├── data/
│   ├── research_plan.json
│   ├── sources.json
│   ├── source_text.json
│   ├── source_chunks.json
│   ├── evaluated_sources.json
│   ├── evidence.json
│   ├── filtered_evidence.json
│   └── research_report.md
│
├── src/
│   ├── planner/
│   │   └── planner.py
│   │
│   ├── retrieval/
│   │   └── retriever.py
│   │
│   ├── evaluation/
│   │   ├── evaluator.py
│   │   └── evidence_filter.py
│   │
│   ├── extraction/
│   │   ├── source_fetcher.py
│   │   ├── chunker.py
│   │   └── extractor.py
│   │
│   └── synthesis/
│       └── synthesizer.py
│
├── .gitignore
├── requirements.txt
└── README.md

Pipeline Components

1. Research Planner
The planner receives the main research question and decomposes it into a set of focused subquestions.
For example:
How are AI agents changing software engineering?

is decomposed into questions covering areas such as:
- repetitive software-development tasks
- code generation and debugging
- human-AI collaboration
- software quality and reliability
- required engineering skills
- ethical considerations
- long-term changes in software engineering
The planner uses the local Qwen model and stores the resulting plan in:
data/research_plan.json

2. Query Generation
For each research subquestion, the system generates targeted search queries.
This allows the system to approach a broad research problem from multiple angles rather than relying on a single search query.

3. Source Retrieval
The retriever executes the generated search queries and collects candidate sources.
The retrieval layer is designed to tolerate individual search failures rather than terminating the entire research process.
Retrieved sources are stored in:
data/sources.json

The retriever finds candidate information; it does not assume that every retrieved source is reliable or relevant.

4. Source Fetching
Search-result snippets are not treated as the final evidence.
The source-fetching stage attempts to obtain the actual content of retrieved web pages.
The extracted source content is stored in:
data/source_text.json

This provides the downstream stages with substantially more context than a search-result snippet alone.

5. Chunking
Long source documents are divided into smaller pieces.
Source Document
      │
      ├── Chunk 1
      ├── Chunk 2
      ├── Chunk 3
      └── ...

The resulting chunks are stored in:
data/source_chunks.json

Chunking makes it possible for later stages to process relevant portions of source documents without passing entire documents through every LLM request.

6. Source Evaluation
The evaluator assesses retrieved source material based on factors such as:
- relevance to the research subquestion
- source quality
- supporting reasoning
The evaluated sources are stored in:
data/evaluated_sources.json

The evaluator is therefore a separate layer from retrieval:
Retrieval
    ↓
Candidate Sources
    ↓
Evaluation
    ↓
Higher-quality / more relevant sources

7. Evidence Extraction
The extraction stage processes source material and identifies evidence that can support research claims.
Evidence is represented in a structured form containing information such as:
{
  "claim": "...",
  "evidence": "...",
  "confidence": 0.0
}

The resulting evidence is stored in:
data/evidence.json

This separates evidence extraction from final report generation.

8. Evidence Filtering
Not every extracted evidence item should automatically reach the final report.
The evidence filter removes evidence that does not meet the system's acceptance criteria.
Example V2 processing:
Total evidence items:     168
Accepted evidence items:  154
Rejected evidence items:   14

The accepted evidence is stored in:
data/filtered_evidence.json

This creates an explicit quality-control stage before synthesis.

9. Research Synthesis
The synthesizer receives the filtered evidence and generates the final research report.
The synthesizer is instructed to:
- use the supplied evidence
- remain aligned with the corresponding research subquestions
- avoid inventing facts or sources
- preserve source traceability
- distinguish between stronger and weaker evidence
- communicate uncertainty where appropriate
The final report is written to:
data/research_report.md

Evidence-Grounded Architecture
A central design principle of this project is that the final report should not be generated from the model's general knowledge alone.
Instead:

External Sources
       ↓
Source Content
       ↓
Evaluated Sources
       ↓
Extracted Evidence
       ↓
Filtered Evidence
       ↓
Final Report

This makes the system closer to an evidence-grounded research pipeline than a conventional conversational chatbot.
The intermediate artifacts also make it possible to inspect where a conclusion came from.

Data Flow
Each major pipeline stage communicates through structured JSON artifacts.

research_plan.json
        ↓
sources.json
        ↓
source_text.json
        ↓
source_chunks.json
        ↓
evaluated_sources.json
        ↓
evidence.json
        ↓
filtered_evidence.json
        ↓
research_report.md

This design provides explicit handoffs between components and makes individual stages easier to inspect, debug, replace, or improve.

Example Research Question
The current research experiment investigates:
How are AI agents changing software engineering?

The system currently approaches this question through seven subquestions covering automation, code generation and debugging, human-AI collaboration, software quality, engineering skills, ethics, and long-term changes.
The final synthesis is generated from the filtered evidence collected by the pipeline.

Local LLM Setup
This project uses Ollama so that the LLM can run locally without requiring a paid API.
Install Ollama and pull the model:
ollama pull qwen3:8b

Verify that the model is available:
ollama list

The project expects the local Ollama runtime to be available when running the LLM-dependent stages.

Installation
Clone the repository:
git clone https://github.com/Code-Sahil/ai-research-system.git
cd ai-research-system

Create a Python virtual environment:
python -m venv .venv

Activate it on Windows:
.venv\Scripts\Activate.ps1

Install dependencies:
pip install -r requirements.txt

Make sure Ollama is installed and the required model is available:
ollama pull qwen3:8b

Running the Pipeline
The individual modules can be executed as separate stages.
The exact execution order follows the pipeline:
Planner
→ Retrieval
→ Source Fetching
→ Chunking
→ Evaluation
→ Extraction
→ Evidence Filtering
→ Synthesis

Each stage consumes artifacts produced by earlier stages.
This modular approach makes it possible to inspect intermediate results instead of treating the entire research process as a single black box.

Version History
V1 — Initial AI Research System
V1 established the basic research pipeline:
Research Question
→ Planning
→ Retrieval
→ Evaluation
→ Synthesis

The first version demonstrated the core concept of using an LLM to perform structured research.

V2 — Evidence Pipeline

V2 expanded the system into a more complete evidence-grounded architecture.
Major improvements include:
- actual source-content retrieval
- source chunking
- evaluation based on source content
- structured evidence extraction
- evidence filtering
- evidence confidence
- stronger source traceability
- improved synthesis instructions
- clearer separation between pipeline stages
- intermediate artifacts for debugging and inspection

The V2 architecture is:
Planning
→ Query Generation
→ Retrieval
→ Source Fetching
→ Chunking
→ Source Evaluation
→ Evidence Extraction
→ Evidence Filtering
→ Synthesis

Engineering Design Principles

Modularity
Each stage has a focused responsibility and is implemented separately.

Explicit Data Contracts
JSON artifacts provide structured interfaces between stages.

Evidence Grounding
The synthesis stage receives filtered evidence rather than relying exclusively on the LLM's pretrained knowledge.

Traceability
Evidence can be associated with the sources from which it was obtained.

Fault Tolerance
Individual retrieval failures should not unnecessarily terminate the complete research process.

Inspectability
Intermediate artifacts are preserved so that pipeline behavior can be examined and debugging does not require treating the entire system as a black box.

Local-First Development
The system uses a local LLM, allowing development without a paid commercial LLM API.

Limitations
This system is an experimental research pipeline and should not be treated as an autonomous authority on a research topic.
Potential limitations include:
- search engines may return incomplete or irrelevant sources
- some web pages may be inaccessible or difficult to extract
- source quality evaluation is performed with an LLM and is therefore imperfect
- extracted evidence can contain errors
- LLM-generated synthesis can still misinterpret evidence
- retrieval coverage depends on the search queries generated
- local model performance is constrained by available hardware
- the current pipeline does not guarantee factual correctness
The system therefore emphasizes evidence collection, filtering, and traceability rather than claiming perfect research accuracy.

Future Development
Planned engineering improvements include:
- automated tests for individual pipeline components
- GitHub Actions CI
- improved logging and error handling
- configuration management
- Docker containerization
- reproducible pipeline execution
- cloud deployment
- monitoring and observability
- improved source-ranking strategies
- stronger evidence validation
- research-result visualization
The long-term goal is to evolve the project from a local research prototype into a reproducible, testable, and deployable AI research system.

Author
Sahil Karkee
Built as a personal AI / software engineering project focused on:
- Artificial Intelligence
- LLM systems
- Retrieval-Augmented Generation
- Information retrieval
- Evidence-grounded generation
- Software engineering
- MLOps / DevOps