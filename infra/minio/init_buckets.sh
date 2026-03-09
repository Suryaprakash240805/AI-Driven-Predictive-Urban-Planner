#!/bin/bash
# Run once after MinIO starts to create required buckets

MC="docker run --rm --network host minio/mc"

# Configure alias
$MC alias set local http://localhost:9000 minioadmin minioadmin

# Create buckets
$MC mb --ignore-existing local/urban-reports
$MC mb --ignore-existing local/urban-layouts

# Set public download policy for layouts (so frontend can render images)
$MC anonymous set download local/urban-layouts

echo "✅ MinIO buckets initialized"
