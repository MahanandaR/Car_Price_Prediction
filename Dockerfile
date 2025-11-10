# ---- Stage 1: Builder ----

# Start with the official Python 3.11 image.
# -slim means this is a smaller Debian-based image with fewer preinstalled packages, which makes it lighter.
# The "AS builder" means this stage will be named "builder" and used later in the final stage to copy built dependencies.
FROM python:3.11-slim AS builder

# Install required system packages for Python libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app inside the container.
# All future commands (COPY, RUN, CMD) will be executed from here.
WORKDIR /app

# Copies your local requirements.txt into the container's /app folder.
COPY requirements.txt .

# Create a custom directory (/install) to hold installed Python packages.
# Install dependencies from requirements.txt into /install instead of the global site-packages.
# --no-cache-dir prevents pip from storing its cache, making the image smaller.
RUN mkdir -p /install && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Copies all the remaining project files (Flask API, HTML, CSS, JS, etc.) into /app.
COPY . .

# ---- Stage 2: Final Image ----

# Start again from the lightweight Python 3.11-slim image.
# This ensures the final image is clean and doesn't include build tools from the builder stage.
FROM python:3.11-slim

# Set the working directory to /app inside the container.
WORKDIR /app

# Copy Installed Python packages from the builder stage into the final image.
# This way, the final image doesn't need to reinstall dependencies.
COPY --from=builder /install /usr/local

# Copy the Application Source code from the builder stage.
COPY . .

# Expose FastAPI port, so it can be accessed from outside the container.
EXPOSE 8000

# Default command to run the FastAPI app with Uvicorn in production mode.
# --host 0.0.0.0 allows external connections (necessary in Docker).
# --port 8000 specifies the port.
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
