FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies using pip
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Run the application
CMD ["python", "app.py"] 