FROM python:3.10-slim

# Create a non-root user (Hugging Face Requirement)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy all files to /app
COPY --chown=user . .

# Hugging Face Space MUST use port 7860
EXPOSE 7860

# Start the server on the correct port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]