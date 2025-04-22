# Use official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Copy only requirements.txt first
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN cat /app/requirements.txt \
    && pip install --upgrade pip \
    && pip install -r /app/requirements.txt \
    && pip list

# Copy the rest of the project files
COPY . .

# Create a virtual environment inside the container
RUN python -m venv .venv

# Use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose FastAPI default port
EXPOSE 8000

# Run the application using uvicorn
CMD ["python", "RestApi/main.py"]