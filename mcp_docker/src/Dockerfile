FROM python:3.12.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV RUNNING_IN_PRODUCTION=1

# Set the working directory
WORKDIR /code

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy only the server code and requirements
COPY server.py /code/
COPY requirements.txt /code/

# Expose port 8080 for the SSE server
EXPOSE 8080

# Start the app with uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]

# Create a non-root user
RUN useradd -m appuser
USER appuser