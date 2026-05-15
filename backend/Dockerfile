FROM python:3.10-slim

# Create a non-root user (Required for Hugging Face Spaces)
RUN useradd -m -u 1000 user

# Set environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory to the user's home directory
WORKDIR $HOME/app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=user . .

# Hugging Face Spaces expose port 7860
EXPOSE 7860

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
