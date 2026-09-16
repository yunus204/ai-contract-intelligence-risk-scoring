FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1


WORKDIR /app


# --------------------------------------------------
# System dependencies
# --------------------------------------------------

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libgl1 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*


# --------------------------------------------------
# Python dependencies
# --------------------------------------------------

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt


# --------------------------------------------------
# spaCy English model
# --------------------------------------------------

RUN python -m spacy download en_core_web_sm


# --------------------------------------------------
# Create non-root application user
# --------------------------------------------------

RUN useradd \
    --create-home \
    --shell /bin/bash \
    appuser


# --------------------------------------------------
# Application source
# --------------------------------------------------

COPY --chown=appuser:appuser . .


# --------------------------------------------------
# Runtime directories
# --------------------------------------------------

RUN mkdir -p \
    /app/data/raw/uploads \
    /app/models \
    && chown -R appuser:appuser \
    /app/data \
    /app/models


# --------------------------------------------------
# Run as non-root
# --------------------------------------------------

USER appuser


EXPOSE 8000


CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]