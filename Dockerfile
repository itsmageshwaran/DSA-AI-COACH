FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml ./

# Copy application code before install so poetry can find it
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
COPY scripts/ scripts/
COPY seed_data.json .
COPY run_demo.py scripts/create_demo_user.py

# Install dependencies (without dev dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

COPY run.sh .
RUN chmod +x run.sh

# Expose default port (Hugging Face Spaces uses 7860)
EXPOSE 7860

# Start the application
CMD ["./run.sh"]
