# ⚖️ AI Contract Intelligence & Risk Scoring

An AI-powered legal contract analysis platform built with **RoBERTa**, **spaCy**, **FastAPI**, **Celery**, **Redis**, **Pinecone**, **React**, and **Docker**.

The platform processes PDF and Word contracts, extracts important legal entities, identifies contract clauses, calculates an explainable risk score, and provides semantic search across uploaded documents.

The system is designed as a production-oriented NLP application with asynchronous document processing, structured logging, Docker deployment, load testing, and a React-based frontend.

---

# 🚀 Features

- ✅ PDF Contract Upload
- ✅ DOCX Contract Upload
- ✅ Scanned PDF OCR
- ✅ Automatic OCR Fallback
- ✅ spaCy Named Entity Recognition
- ✅ Organization Extraction
- ✅ Date Extraction
- ✅ Monetary Value Extraction
- ✅ Person Extraction
- ✅ Jurisdiction Extraction
- ✅ RoBERTa Legal Clause Classification
- ✅ 41 CUAD Legal Clause Categories
- ✅ Multi-Label Classification
- ✅ Clause Confidence Scores
- ✅ Explainable Contract Risk Scoring
- ✅ Risk Factor Breakdown
- ✅ Evidence Text for Detected Clauses
- ✅ Pinecone Vector Database
- ✅ Semantic Contract Search
- ✅ Sentence Transformer Embeddings
- ✅ FastAPI REST API
- ✅ Swagger / OpenAPI Documentation
- ✅ Celery Background Processing
- ✅ Redis Task Queue
- ✅ Task Progress Tracking
- ✅ React + Vite Frontend
- ✅ Docker & Docker Compose
- ✅ Non-Root Docker Containers
- ✅ Structured JSON Logging
- ✅ Request ID Tracking
- ✅ Celery Task Tracing
- ✅ API Load Testing with Locust
- ✅ End-to-End Pipeline Benchmarking
- ✅ Production Health Checks

---

# 🏗️ System Architecture

```text
                         User
                          │
                          ▼
                  React Frontend
                          │
                          ▼
                     FastAPI API
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
          Redis Queue             Pinecone
              │                 Vector Database
              ▼                       ▲
        Celery Worker                 │
              │                       │
              ▼                       │
      Document Processing             │
      ┌───────┼────────┐              │
      │       │        │              │
      ▼       ▼        ▼              │
   PyMuPDF  DOCX   Tesseract OCR      │
      │                │              │
      └───────┬────────┘              │
              ▼                       │
        Extracted Text                │
              │                       │
       ┌──────┴─────────┐             │
       │                │             │
       ▼                ▼             │
   spaCy NER      RoBERTa Classifier  │
       │                │             │
       │                ▼             │
       │          Clause Detection    │
       │                │             │
       │                ▼             │
       │           Risk Scoring       │
       │                              │
       └──────────┬───────────────────┘
                  ▼
         Sentence Transformer
                  │
                  ▼
              Pinecone
```

---

# 🔄 Contract Processing Workflow

```text
Upload PDF / DOCX
       │
       ▼
FastAPI validates file
       │
       ▼
File stored locally
       │
       ▼
Task sent to Redis
       │
       ▼
Celery Worker
       │
       ▼
Document Extraction
       │
       ├── PyMuPDF
       ├── python-docx
       └── Tesseract OCR
       │
       ▼
spaCy Entity Extraction
       │
       ▼
RoBERTa Clause Classification
       │
       ▼
Risk Scoring Engine
       │
       ▼
Sentence Transformer Embeddings
       │
       ▼
Pinecone Vector Index
       │
       ▼
Analysis Result
       │
       ▼
React Dashboard
```

---

# 📂 Project Structure

```text
ai-contract-intelligence-risk-scoring/
│
├── backend/
│   └── app/
│       │
│       ├── api/
│       │   ├── contracts.py
│       │   └── search.py
│       │
│       ├── schemas/
│       │   └── search.py
│       │
│       ├── services/
│       │   ├── document_processor.py
│       │   ├── entity_extractor.py
│       │   ├── clause_classifier.py
│       │   ├── risk_scoring.py
│       │   ├── vector_search.py
│       │   ├── cuad_preprocessor.py
│       │   ├── train_legal_ner.py
│       │   ├── train_clause_classifier.py
│       │   └── tune_clause_threshold.py
│       │
│       ├── tasks/
│       │   └── contract_tasks.py
│       │
│       ├── utils/
│       │   └── logging_config.py
│       │
│       ├── celery_app.py
│       └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── api.js
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   ├── cuad/
│   ├── processed/
│   └── raw/
│
├── models/
│   ├── legal_ner/
│   └── clause_classifier/
│
├── docs/
│   └── performance.md
│
├── tests/
│   ├── create_scanned_pdf.py
│   ├── test_document_processor.py
│   ├── test_legal_ner.py
│   ├── test_vector_search.py
│   │
│   └── load/
│       ├── locustfile.py
│       └── pipeline_benchmark.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙️ Technologies Used

## 🧠 NLP & Machine Learning

- Python 3.12
- PyTorch
- Hugging Face Transformers
- RoBERTa
- spaCy
- Sentence Transformers
- scikit-learn

## 📄 Document Processing

- PyMuPDF
- Tesseract OCR
- pdf2image
- Poppler
- python-docx

## 🔎 Semantic Search

- Pinecone
- LangChain
- Hugging Face Embeddings
- sentence-transformers/all-MiniLM-L6-v2

## ⚡ Backend

- FastAPI
- Uvicorn
- Celery
- Redis
- Pydantic

## 🎨 Frontend

- React
- Vite
- Axios
- CSS

## 🐳 Infrastructure

- Docker
- Docker Compose
- AWS EC2
- Structured JSON Logging

## 🧪 Testing

- Locust
- Swagger / OpenAPI
- Python Integration Tests
- Pipeline Benchmarking

---

# 📊 Dataset

The project uses the **Contract Understanding Atticus Dataset (CUAD)**.

CUAD is a legal contract dataset containing commercial agreements annotated across multiple legal clause categories.

## Processed Dataset Statistics

| Metric | Value |
|---|---:|
| Contracts | 510 |
| Legal Categories | 41 |
| QA Examples | 20,910 |
| Answer Annotations | 13,823 |
| Answered Examples | 6,702 |
| No-Answer Examples | 14,208 |
| Classification Records | ~26,952 |

---

# 🧠 Clause Classification Model

The contract clause classifier is based on:

```text
RoBERTa
   │
   ▼
CUAD Training Data
   │
   ▼
Overlapping Contract Chunks
   │
   ▼
Transformer Tokenization
   │
   ▼
Multi-Label Classification
   │
   ▼
Sigmoid Probabilities
   │
   ▼
Confidence Threshold
   │
   ▼
Detected Legal Clauses
```

---

# 🏷️ CUAD Clause Categories

The model supports **41 legal clause categories**.

Examples include:

- Agreement Date
- Effective Date
- Expiration Date
- Parties
- Governing Law
- Anti-Assignment
- Audit Rights
- Cap On Liability
- Exclusivity
- License Grant
- Minimum Commitment
- Non-Compete
- Non-Transferable License
- Notice Period To Terminate Renewal
- Post-Termination Services
- Revenue / Profit Sharing
- Source Code Escrow
- Warranty Duration
- Change Of Control
- Most Favored Nation

---

# ⚠️ Risk Scoring Engine

Detected clauses are passed to an explainable risk-scoring engine.

The score is based on:

```text
Clause Detection
       │
       ▼
Model Confidence
       │
       ▼
Clause Risk Weight
       │
       ▼
Risk Contribution
       │
       ▼
Overall Risk Score
```

The system generates:

- Overall risk score
- Risk level
- Top risk factors
- Clause confidence
- Individual risk contribution

---

# 📈 Risk Levels

```text
0 ───────────────────────────── 100

Low     Medium      High       Critical
```

Risk levels:

- 🟢 Low
- 🟡 Medium
- 🟠 High
- 🔴 Critical

The risk score is intended as an AI-assisted review indicator and not as a legal judgment.

---

# 🧾 Named Entity Recognition

The spaCy-based NER pipeline extracts:

```text
Organizations
Dates
Money
Persons
Jurisdictions
```

Example:

```json
{
    "organizations": [
        "Acme Corporation",
        "Global Technologies Ltd."
    ],
    "dates": [
        "January 15, 2026",
        "December 31, 2028"
    ],
    "money": [
        "$250,000"
    ],
    "jurisdictions": [
        "State of California"
    ]
}
```

---

# 📄 OCR Support

The document pipeline first attempts normal text extraction.

```text
PDF
 │
 ▼
PyMuPDF
 │
 ├── Enough text ───────► Continue
 │
 └── Insufficient text
          │
          ▼
      pdf2image
          │
          ▼
      Tesseract OCR
          │
          ▼
      Extracted Text
```

This allows the platform to process both:

- Digital PDFs
- Scanned / image-only PDFs

---

# 🔎 Semantic Search

Contracts are split into overlapping chunks and converted into dense embeddings.

Embedding model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Embedding dimension:

```text
384
```

Vector database:

```text
Pinecone
```

Similarity metric:

```text
Cosine Similarity
```

Example query:

```text
What does this contract say about legal risk and liability?
```

The application retrieves the contract sections that are semantically most relevant to the query.

---

# ⚡ Asynchronous Processing

Contract processing is handled asynchronously.

FastAPI does not wait for the entire machine-learning pipeline.

Instead:

```text
FastAPI
   │
   ▼
Redis
   │
   ▼
Celery
   │
   ▼
AI Processing
```

The upload endpoint immediately returns:

```json
{
    "contract_id": "fac627bc-e09b-4b4b-ba36-d6e99b37fce7",
    "filename": "sample_contract.pdf",
    "task_id": "a58777c4-1725-4eec-9b12-e0a7acfcf82a",
    "status": "queued"
}
```

The frontend then polls the task-status API.

---

# 📊 Processing Progress

Example processing stages:

```text
Document Extraction      20%
Entity Extraction        45%
Clause Classification    65%
Risk Scoring             75%
Vector Indexing          85%
Finalizing               95%
Completed               100%
```

---

# 🌐 REST API

The backend is built using FastAPI.

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 📤 Upload Contract

```http
POST /api/contracts/upload
```

Supported file types:

```text
.pdf
.docx
```

Example response:

```json
{
    "contract_id": "uuid",
    "filename": "contract.pdf",
    "task_id": "uuid",
    "status": "queued",
    "message": "Contract uploaded successfully. Processing has started in the background."
}
```

HTTP status:

```text
202 Accepted
```

---

# 🔄 Check Task Status

```http
GET /api/contracts/tasks/{task_id}
```

Possible task states:

```text
PENDING
STARTED
PROCESSING
SUCCESS
FAILURE
```

Example:

```json
{
    "task_id": "uuid",
    "status": "PROCESSING",
    "stage": "clause_classification",
    "progress": 65
}
```

---

# 🔍 Semantic Search API

```http
POST /api/search
```

Example request:

```json
{
    "contract_id": "uuid",
    "query": "What does this contract say about termination?",
    "top_k": 5
}
```

Example response:

```json
{
    "contract_id": "uuid",
    "query": "What does this contract say about termination?",
    "result_count": 3,
    "results": [
        {
            "rank": 1,
            "score": 0.3747,
            "text": "Relevant contract section..."
        }
    ]
}
```

---

# 🎨 React Frontend

The React dashboard provides:

- Contract upload
- Processing progress
- Overall risk score
- Risk level
- Extracted entities
- Risk factors
- Detected clauses
- Confidence scores
- Clause evidence
- Semantic contract search

Frontend URL:

```text
http://localhost:5173
```

Backend URL:

```text
http://127.0.0.1:8000
```

---

# 📦 Installation

Clone the repository:

```bash
git clone https://github.com/yunus204/ai-contract-intelligence-risk-scoring.git
cd ai-contract-intelligence-risk-scoring
```

---

# 🐍 Create Virtual Environment

Windows:

```powershell
py -3.12 -m venv venv
```

Activate:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create:

```text
.env
```

using:

```text
.env.example
```

Example:

```env
PINECONE_API_KEY=your_pinecone_api_key

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

TESSERACT_CMD=path_to_tesseract
POPPLER_PATH=path_to_poppler

CLAUSE_THRESHOLD=0.45

LOG_LEVEL=INFO
```

Never commit `.env`.

---

# ▶️ Run Without Docker

## Start Redis

```powershell
docker run -d `
  --name contract-intelligence-redis `
  -p 6379:6379 `
  redis:7-alpine
```

---

## Start Celery

```powershell
celery -A backend.app.celery_app.celery_app worker --loglevel=info --pool=solo
```

Expected:

```text
Connected to redis://localhost:6379/0

[tasks]
  . process_contract

celery@... ready.
```

---

## Start FastAPI

```powershell
uvicorn backend.app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## Start React Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

---

# 🐳 Run With Docker

The recommended way to run the backend is Docker Compose.

Build:

```powershell
docker compose build
```

Start:

```powershell
docker compose up -d
```

Check containers:

```powershell
docker compose ps
```

Expected:

```text
contract-intelligence-api       Up (healthy)

contract-intelligence-celery    Up

contract-intelligence-redis     Up (healthy)
```

---

# 🩺 Health Check

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected:

```text
status
------
healthy
```

---

# 🔒 Docker Security

The API and Celery containers run using a dedicated non-root user:

```text
appuser
```

Check:

```powershell
docker compose exec api whoami
docker compose exec celery whoami
```

Expected:

```text
appuser
appuser
```

Production Docker features include:

- Non-root containers
- Health checks
- Restart policies
- Graceful shutdown
- Redis health monitoring
- `.dockerignore`
- Environment variables
- Structured logging

---

# 📋 Structured Logging

API and worker logs are emitted in structured JSON format.

Example:

```json
{
    "timestamp": "2026-09-16T17:16:40.180202+00:00",
    "level": "INFO",
    "logger": "contract_intelligence.api",
    "message": "HTTP request completed",
    "request_id": "5f9cb194-eb7e-4889-a0ee-62b68b9708d3",
    "method": "GET",
    "path": "/health",
    "status_code": 200,
    "duration_ms": 0.78
}
```

---

# 🔄 Celery Task Logging

Every contract is traceable using:

```text
task_id
contract_id
stage
```

Example stages:

```text
Contract processing started

Document extraction started

Document extraction completed

Entity extraction started

Entity extraction completed

Clause classification started

Clause classification completed

Risk scoring started

Risk scoring completed

Vector indexing started

Vector indexing completed

Contract processing completed
```

---

# 🧪 Load Testing

The API was tested using **Locust**.

Test configuration:

```text
Concurrent Users: 20

Spawn Rate: 2 users / second

Endpoints:
GET /
GET /health
```

---

# 📈 API Load Test Results

| Metric | Result |
|---|---:|
| Total Requests | 2,876 |
| Failed Requests | 0 |
| Failure Rate | 0% |
| Median Response Time | 4 ms |
| Average Response Time | 4.51 ms |
| P95 Response Time | 7 ms |
| P99 Response Time | 11 ms |
| Maximum Response Time | 24 ms |
| Observed Throughput | ~11.8 req/s |

No HTTP failures occurred during the test.

---

# ⏱️ AI Pipeline Benchmark

The full AI pipeline was benchmarked using three sequential contract-processing runs.

| Run | Queue Time | Processing Time | Total Time |
|---|---:|---:|---:|
| Run 1 | 0.124 s | 19.88 s | 20.00 s |
| Run 2 | 0.059 s | 6.08 s | 6.14 s |
| Run 3 | 0.026 s | 7.13 s | 7.16 s |

Summary:

```text
Successful Runs: 3 / 3

Average End-to-End Time: 11.10 seconds

Fastest Run: 6.14 seconds

Slowest Run: 20.00 seconds

Warm-Run Average: ~6.65 seconds
```

The first run contains additional cold-start and cache warm-up overhead.

---

# 🧪 Run Load Test

Install:

```powershell
pip install locust
```

Run:

```powershell
locust -f tests/load/locustfile.py --host http://127.0.0.1:8000
```

Open:

```text
http://localhost:8089
```

---

# 🧪 Run Pipeline Benchmark

```powershell
python tests/load/pipeline_benchmark.py
```

---

# 📋 Example Final Analysis Output

```json
{
    "contract_id": "fac627bc-e09b-4b4b-ba36-d6e99b37fce7",

    "filename": "sample_contract.pdf",

    "entities": {
        "organizations": [],
        "dates": [],
        "money": [],
        "jurisdictions": [],
        "persons": []
    },

    "clause_analysis": {
        "threshold": 0.45,
        "chunks_analyzed": 9,
        "detected_clauses": []
    },

    "risk_analysis": {
        "risk_score": 0,
        "risk_level": "low",
        "risk_factors": [],
        "method": "CUAD clause confidence + heuristic legal risk weights"
    },

    "vector_index": {
        "indexed": true,
        "namespace": "contract-id",
        "chunks": 9
    },

    "status": "completed"
}
```

---

# 🧠 Model Training

The clause classifier training pipeline uses:

```text
RoBERTa
+
CUAD
+
PyTorch
+
Weighted BCE Loss
+
Multi-Label Classification
```

Training configuration includes:

- 41 labels
- Contract-level train/validation split
- Weighted BCE loss
- Maximum token length of 512
- Learning rate of `2e-5`
- Threshold tuning
- Precision evaluation
- Recall evaluation
- F1 evaluation

---

# 🎯 Threshold Tuning

The initial smoke-test classifier was evaluated across multiple thresholds.

The best smoke-test threshold was:

```text
0.45
```

This threshold is configurable:

```env
CLAUSE_THRESHOLD=0.45
```

The final threshold should be recalibrated after full GPU training.

---

# ⚠️ Current Model Status

The complete machine-learning training pipeline is implemented.

The current local model is a **smoke-test checkpoint** used to validate the full application architecture.

```text
Application Architecture       ✅ Complete

Document Processing            ✅ Complete

NER                            ✅ Complete

Clause Inference Integration   ✅ Complete

Risk Scoring                   ✅ Complete

Semantic Search                ✅ Complete

Frontend                       ✅ Complete

Docker Deployment              ✅ Complete

Final Full CUAD Training       ⏳ Pending GPU availability
```

The current smoke-test model should **not** be treated as a final production-quality legal classifier.

---

# ☁️ AWS Deployment

The project is designed for deployment on AWS EC2.

Target architecture:

```text
                     Internet
                        │
                        ▼
                  React Frontend
                        │
                        ▼
                    FastAPI
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
           Redis                Pinecone
             │
             ▼
        Celery Worker
             │
      ┌──────┼───────┐
      │      │       │
      ▼      ▼       ▼
   spaCy  RoBERTa   OCR
```

GPU EC2 infrastructure is intended for the final RoBERTa training stage.

The application itself can run on CPU infrastructure.

---

# 🛡️ Security Considerations

Implemented:

- `.env` excluded from Git
- API keys stored in environment variables
- Non-root Docker containers
- Request IDs
- Structured application logs
- File extension validation
- Health checks
- Container restart policies
- Restricted frontend CORS origins
- Background task isolation

Recommended for a full production deployment:

- HTTPS
- Authentication
- Role-Based Access Control
- Rate Limiting
- AWS Secrets Manager
- Private Redis Network
- Encrypted Storage
- S3 Document Storage
- CloudWatch Monitoring

---

# 📌 Current Capabilities

- Upload legal PDF and DOCX documents
- Process scanned contracts using OCR
- Extract contract text
- Detect organizations
- Detect dates
- Detect monetary values
- Detect persons
- Detect jurisdictions
- Identify CUAD legal clauses
- Calculate contract risk scores
- Rank important risk factors
- Display clause confidence
- Show evidence text
- Generate contract embeddings
- Store vectors in Pinecone
- Perform semantic search
- Process documents asynchronously
- Track task progress
- Display results in a React dashboard
- Run services using Docker
- Generate structured production logs
- Handle concurrent API requests
- Benchmark ML processing latency

---

# ⚠️ Limitations

- Final RoBERTa accuracy depends on full CUAD GPU training.
- The current classifier checkpoint is primarily for integration testing.
- Risk scores use heuristic legal-risk weights.
- Risk scores should not be considered legal judgments.
- OCR performance depends on scan quality.
- NER performance may vary across contract formats.
- Semantic search quality depends on embeddings and chunking.
- User authentication is not currently implemented.
- The system is intended as legal-review assistance, not a replacement for professional legal review.

---

# 🔮 Future Improvements

- Full CUAD GPU Fine-Tuning
- Legal-Domain Transformer Models
- Per-Clause Threshold Calibration
- Better Legal NER Dataset
- PDF Clause Highlighting
- Contract Comparison
- Contract Summarization
- Retrieval-Augmented Generation
- Cross-Encoder Reranking
- Authentication
- Role-Based Access Control
- PostgreSQL Database
- AWS S3 Document Storage
- AWS CloudWatch Monitoring
- AWS Secrets Manager
- CI/CD With GitHub Actions
- Horizontal Celery Scaling
- Kubernetes Deployment
- Email Risk Reports
- Downloadable Contract Analysis Reports

---

# 🔄 Git Development Workflow

The project follows feature-based Git development.

Branches used include:

```text
feature/project-setup

feature/cuad-data-pipeline

feature/transformer-tokenization

feature/document-ingestion

feature/spacy-ner

feature/roberta-clause-classifier

feature/vector-search

feature/fastapi-api

feature/celery-processing

feature/clause-risk-analysis

feature/docker-deployment

feature/frontend-dashboard

feature/production-hardening

feature/load-testing

feature/deployment-hardening

feature/final-documentation
```

Features are merged into:

```text
develop
```

before the final production merge.

---

# 📊 Project Status

```text
CUAD Dataset Processing        ✅ Complete

PDF Processing                 ✅ Complete

DOCX Processing                ✅ Complete

Tesseract OCR                  ✅ Complete

spaCy NER                      ✅ Complete

RoBERTa Training Pipeline      ✅ Complete

Clause Classification          ✅ Complete

Risk Scoring                   ✅ Complete

Pinecone Vector Search         ✅ Complete

FastAPI                        ✅ Complete

Redis                          ✅ Complete

Celery                         ✅ Complete

React Frontend                 ✅ Complete

Docker                         ✅ Complete

Structured Logging             ✅ Complete

Load Testing                   ✅ Complete

Performance Benchmarking       ✅ Complete

Production Hardening           ✅ Complete

Final GPU Training             ⏳ Pending

AWS Cloud Deployment           ⏳ Final Stage
```

---

# ⚖️ Legal Disclaimer

This application is intended for:

- Educational purposes
- Research
- Contract-review assistance
- Machine-learning experimentation

AI-generated:

- Clause classifications
- Entity predictions
- Risk scores
- Search results

do **not** constitute legal advice.

Important contracts and legal decisions should always be reviewed by qualified legal professionals.

---

# 🤖 AI Assistance Disclosure

AI coding assistance was used during development to:

- Understand machine-learning concepts
- Debug Python and Docker issues
- Review architecture
- Improve code structure
- Troubleshoot FastAPI and Celery
- Assist with documentation
- Review implementation decisions

The project architecture, codebase, ML pipeline, API workflow, Docker setup, and implementation decisions can be explained and demonstrated by the developer.

---

# 👨‍💻 Developer

Developed as a production-level **Data Science & Machine Learning project** focused on:

- Natural Language Processing
- Legal AI
- Machine Learning
- Deep Learning
- FastAPI
- React
- Docker
- Vector Databases
- Production ML Engineering

GitHub:

```text
https://github.com/yunus204
```

Project Repository:

```text
https://github.com/yunus204/ai-contract-intelligence-risk-scoring
```

---

# 📄 License

This project is intended primarily for educational, research, and portfolio purposes.

Use of legal documents and AI-generated contract analysis should comply with applicable privacy, data-protection, contractual, and legal requirements.