FROM python:3.11-slim

WORKDIR /app

# System deps for geospatial and torch
RUN apt-get update && apt-get install -y \
    gdal-bin libgdal-dev gcc g++ git \
    libgeos-dev libproj-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only torch first (smaller image)
RUN pip install --no-cache-dir torch==2.2.1 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir torch-geometric==2.5.1
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
