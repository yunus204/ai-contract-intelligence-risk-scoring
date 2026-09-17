# AWS Deployment Guide

## AI-Powered Contract Intelligence & Risk Scoring

This document describes the production deployment of the AI Contract Intelligence platform on Amazon Web Services (AWS).

The deployed application provides:

- React-based web interface
- FastAPI REST API
- Celery asynchronous processing
- Redis task queue
- spaCy legal entity extraction
- RoBERTa-based clause classification
- Risk scoring
- Pinecone semantic search
- Nginx reverse proxy
- Dockerized backend services

---

## 1. Deployment Architecture

The production deployment uses a single AWS EC2 instance.

```text
                           Internet
                              |
                              |
                       HTTP Port 80
                              |
                              v
                        +-----------+
                        |   Nginx   |
                        +-----------+
                         /         \
                        /           \
                       v             v
              React Frontend      /api/*
                                  /health
                                  /docs
                                     |
                                     v
                               FastAPI :8000
                                     |
                       +-------------+-------------+
                       |                           |
                       v                           v
                    Celery                      Pinecone
                       |
                       v
                     Redis
                       |
             +---------+----------+
             |                    |
             v                    v
         spaCy NER        RoBERTa Classifier
```

Nginx is the public-facing web server.

FastAPI remains accessible internally on port `8000`, while Redis remains internal to the Docker network.

---

## 2. AWS Infrastructure

### Region

```text
Asia Pacific (Mumbai)
ap-south-1
```

### EC2 Instance

```text
Name: contract-intelligence-production
Instance Type: m7i-flex.large
Architecture: x86_64
vCPU: 2
Memory: 8 GiB
Operating System: Ubuntu Server 26.04 LTS
Storage: 40 GiB gp3
```

The deployment was validated on the EC2 instance using approximately:

```text
7.6 GiB RAM
38 GiB usable root filesystem
```

---

## 3. Security Group Configuration

The production security group follows the principle of exposing only required services.

### Public Inbound Rules

| Service | Port | Source | Purpose |
|---|---:|---|---|
| SSH | 22 | Administrator IP only | Server administration |
| HTTP | 80 | `0.0.0.0/0` | Public application |
| HTTPS | 443 | `0.0.0.0/0` | Reserved for TLS/HTTPS |

### Ports Not Publicly Exposed

```text
8000 - FastAPI
6379 - Redis
```

FastAPI is accessed through Nginx.

Redis is accessed only through the internal Docker network.

---

## 4. Server Preparation

Connect to the EC2 instance:

```bash
ssh -i contract-intelligence-key.pem ubuntu@<PUBLIC_IP>
```

Update the server:

```bash
sudo apt update
sudo apt upgrade -y
```

Install Git and Docker:

```bash
sudo apt install -y git curl ca-certificates docker.io docker-compose-v2
```

Enable Docker:

```bash
sudo systemctl enable --now docker
```

Add the Ubuntu user to the Docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Verify installation:

```bash
git --version
docker --version
docker compose version
```

---

## 5. Clone the Repository

```bash
cd ~
git clone https://github.com/yunus204/ai-contract-intelligence-risk-scoring.git
cd ai-contract-intelligence-risk-scoring
```

Verify the repository:

```bash
git status
```

---

## 6. Production Environment Variables

The `.env` file is intentionally excluded from Git.

Create the environment configuration:

```bash
cp .env.example .env
nano .env
```

Production configuration:

```env
TESSERACT_CMD=/usr/bin/tesseract
POPPLER_PATH=/usr/bin

PINECONE_API_KEY=<YOUR_PINECONE_API_KEY>
PINECONE_INDEX_NAME=contract-intelligence

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

Secure the environment file:

```bash
chmod 600 .env
```

Secrets must never be committed to Git.

---

## 7. Model Deployment

The trained model artifacts are excluded from Git because of their size.

The following model directories must be transferred separately to the EC2 instance:

```text
models/
├── clause_classifier/
└── legal_ner/
```

Example transfer from Windows PowerShell:

```powershell
scp -i "$HOME\Downloads\contract-intelligence-key.pem" -r `
.\models\legal_ner `
ubuntu@<PUBLIC_IP>:~/ai-contract-intelligence-risk-scoring/models/
```

```powershell
scp -i "$HOME\Downloads\contract-intelligence-key.pem" -r `
.\models\clause_classifier `
ubuntu@<PUBLIC_IP>:~/ai-contract-intelligence-risk-scoring/models/
```

Deployed model sizes were approximately:

```text
clause_classifier    480 MB
legal_ner             15 MB
```

---

## 8. Docker Deployment

Build the application images:

```bash
docker compose build
```

Start all backend services:

```bash
docker compose up -d
```

Verify:

```bash
docker compose ps
```

Expected services:

```text
contract-intelligence-api
contract-intelligence-celery
contract-intelligence-redis
```

The API and Redis containers include health checks.

---

## 9. Redis Security

Redis must not be published to the public EC2 interface.

The Redis service communicates internally using:

```text
redis://redis:6379/0
redis://redis:6379/1
```

The Redis Docker configuration therefore does not expose:

```text
0.0.0.0:6379
```

A correct `docker compose ps` output shows Redis as:

```text
6379/tcp
```

rather than a public host mapping.

---

## 10. Backend Validation

Test FastAPI directly from the EC2 host:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

This confirms that FastAPI is operational before configuring Nginx.

---

## 11. React Production Build

Move to the frontend:

```bash
cd ~/ai-contract-intelligence-risk-scoring/frontend
```

Create the production frontend environment:

```bash
printf "VITE_API_URL=/\n" > .env.production
```

Install dependencies:

```bash
npm install
```

Create the production build:

```bash
npm run build
```

The generated production files are stored in:

```text
frontend/dist/
```

Example output:

```text
dist/
├── index.html
├── assets/
├── favicon.svg
└── icons.svg
```

---

## 12. Nginx Installation

Install Nginx:

```bash
sudo apt install -y nginx
```

Verify:

```bash
sudo systemctl status nginx
```

Copy the React build:

```bash
sudo mkdir -p /var/www/contract-intelligence
sudo cp -r dist/* /var/www/contract-intelligence/
```

---

## 13. Nginx Reverse Proxy Configuration

Create:

```text
/etc/nginx/sites-available/contract-intelligence
```

Configuration:

```nginx
server {
    listen 80;
    listen [::]:80;

    server_name _;

    root /var/www/contract-intelligence;
    index index.html;

    client_max_body_size 50M;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_read_timeout 300s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
    }

    location = /health {
        proxy_pass http://127.0.0.1:8000/health;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;

        proxy_set_header Host $host;
    }

    location = /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;

        proxy_set_header Host $host;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Enable the configuration:

```bash
sudo ln -sf \
/etc/nginx/sites-available/contract-intelligence \
/etc/nginx/sites-enabled/contract-intelligence
```

Disable the default site:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
```

Validate:

```bash
sudo nginx -t
```

Reload:

```bash
sudo systemctl reload nginx
```

---

## 14. Production Endpoints

After deployment, the application is available through Nginx.

### Frontend

```text
http://<PUBLIC_IP>
```

### Health Check

```text
http://<PUBLIC_IP>/health
```

Expected:

```json
{"status":"healthy"}
```

### Swagger API Documentation

```text
http://<PUBLIC_IP>/docs
```

### Contract Upload

```text
POST /api/contracts/upload
```

### Task Status

```text
GET /api/contracts/tasks/{task_id}
```

### Semantic Search

```text
POST /api/search
```

---

## 15. End-to-End Production Validation

The complete deployed pipeline was validated using contract uploads through the public React interface.

The tested workflow was:

```text
Contract Upload
      |
      v
FastAPI
      |
      v
Celery Task Queue
      |
      v
Document Extraction
      |
      +------------------+
      |                  |
      v                  v
  spaCy NER        Clause Classifier
      |                  |
      +---------+--------+
                |
                v
           Risk Scoring
                |
                v
        Pinecone Indexing
                |
                v
        React Results UI
```

Production validation confirmed:

- PDF upload
- DOCX/PDF processing pipeline
- asynchronous Celery execution
- entity extraction
- clause classification
- risk-score generation
- Pinecone vector indexing
- semantic search
- React result rendering
- Nginx reverse proxy
- Swagger documentation
- health monitoring

A real legal-contract test was completed successfully through the AWS-hosted frontend.

---

## 16. Application Monitoring

Check running containers:

```bash
docker compose ps
```

View API logs:

```bash
docker compose logs --tail=100 api
```

View Celery logs:

```bash
docker compose logs --tail=100 celery
```

View Redis logs:

```bash
docker compose logs --tail=100 redis
```

Follow API logs:

```bash
docker compose logs -f api
```

Check Nginx:

```bash
sudo systemctl status nginx
```

---

## 17. Restart Procedure

After an EC2 restart:

```bash
cd ~/ai-contract-intelligence-risk-scoring
docker compose up -d
sudo systemctl start nginx
```

Verify:

```bash
docker compose ps
curl http://localhost/health
```

---

## 18. Updating the Application

Pull updated code:

```bash
cd ~/ai-contract-intelligence-risk-scoring
git pull
```

Rebuild backend containers when backend dependencies or source code change:

```bash
docker compose build
docker compose up -d
```

For frontend changes:

```bash
cd frontend
npm install
npm run build
sudo rm -rf /var/www/contract-intelligence/*
sudo cp -r dist/* /var/www/contract-intelligence/
sudo systemctl reload nginx
```

---

## 19. Production Security Measures

The deployment includes the following safeguards:

- `.env` excluded from Git
- Pinecone API key stored only on the server
- `.env` permissions restricted with `chmod 600`
- Redis not exposed publicly
- FastAPI port 8000 not exposed publicly
- SSH restricted to administrator access
- public traffic enters through Nginx
- application processes run inside Docker containers
- Docker application image uses a non-root application user
- request and task logging enabled
- API health checks enabled

---

## 20. HTTPS

The current deployment is accessible through HTTP.

Port `443` is reserved in the AWS security group for a future HTTPS configuration.

Production TLS can be added after assigning a domain name using:

- Nginx
- Let's Encrypt
- Certbot

Until a domain and TLS certificate are configured, browsers may display the application as **Not Secure**.

---

## 21. Model Limitation

The currently deployed RoBERTa classifier is the smoke/integration model used to validate the complete ML engineering pipeline.

It demonstrates:

- model loading
- inference
- multi-label clause prediction
- risk-score integration
- asynchronous processing
- production deployment

The current classifier should not be treated as a production-quality legal decision system.

Full GPU fine-tuning on the complete CUAD-derived training dataset is planned as a model-improvement step.

The application therefore includes the disclaimer:

> AI-generated contract analysis is intended for review assistance and should not be considered legal advice.

---

## 22. Deployment Status

| Component | Status |
|---|---|
| AWS EC2 | ✅ Deployed |
| Docker | ✅ Running |
| FastAPI | ✅ Running |
| Celery | ✅ Running |
| Redis | ✅ Running |
| React | ✅ Deployed |
| Nginx | ✅ Running |
| spaCy NER | ✅ Integrated |
| RoBERTa Clause Classifier | ✅ Integrated |
| Risk Scoring | ✅ Integrated |
| Pinecone | ✅ Integrated |
| Semantic Search | ✅ Working |
| Swagger | ✅ Available |
| End-to-End Contract Test | ✅ Passed |
| Public HTTPS | ⏳ Future enhancement |
| Full GPU Model Training | ⏳ Future enhancement |

---

## 23. Production Result

The project has been successfully deployed as an end-to-end AI contract intelligence platform on AWS EC2.

The deployed system supports the complete workflow:

```text
Upload
   ↓
Extract
   ↓
Understand
   ↓
Classify
   ↓
Score Risk
   ↓
Index
   ↓
Search
   ↓
Review
```

This deployment demonstrates the integration of NLP, deep learning, asynchronous processing, vector search, REST APIs, containerization, cloud infrastructure, and a production web interface in a single working system.