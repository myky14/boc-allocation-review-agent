# Use Python 3.13 slim base image
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary into the image using a pinned stable version
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /uvx /bin/

# Set environment variables
ENV PORT=8080 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    BOC_ENV=production \
    BOC_SKILL_FILE_PATH=SKILL.md

# Set the working directory
WORKDIR /app

# Copy dependency files first for Hatchling package layer caching
COPY pyproject.toml uv.lock ./

# Install project dependencies using uv (exclude dev dependencies and skip installing project package)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source code and relevant data/documentation after dependency sync
COPY boc_agent/ ./boc_agent/
COPY data/ ./data/
COPY docs/ ./docs/
COPY app.py README.md PROJECT_CONTEXT.md walkthrough.md SKILL.md ./

# Create a non-root user for security hygiene
RUN useradd -u 10001 -m appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run the Streamlit application Headless using uv run --no-sync to prevent runtime reinstalls
CMD ["sh", "-c", "uv run --no-sync streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true"]
