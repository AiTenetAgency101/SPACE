#!/bin/bash
# Test script for Atmospheric Grid

echo "=== Atmospheric Grid Test Suite ==="
echo ""

# Wait for service to be ready
echo "Waiting for service to start..."
sleep 5

# Health check
echo "1. Health Check:"
curl -s http://localhost:8000/health | python -m json.tool
echo ""

# Ingest satellite frame
echo "2. Ingesting Himawari satellite frame..."
curl -s -X POST "http://localhost:8000/ingest/satellite-frame?satellite_name=Himawari&region=Japan&band=IR&timestamp=2026-04-17T10:32:00Z&width=2048&height=2048" | python -m json.tool
echo ""

# Get tiles summary
echo "3. Tiles Summary:"
curl -s http://localhost:8000/tiles/summary | python -m json.tool
echo ""

# Get witness ledger summary
echo "4. Witness Ledger Summary:"
curl -s http://localhost:8000/witness/ledger-summary | python -m json.tool
echo ""

# Query witnessed tiles
echo "5. Query Witnessed Tiles (Himawari):"
curl -s "http://localhost:8000/query/witnessed-tiles?satellite=Himawari&limit=5" | python -m json.tool
echo ""

# System info
echo "6. System Information:"
curl -s http://localhost:8000/info | python -m json.tool
echo ""

# Ingest GOES frame
echo "7. Ingesting GOES satellite frame..."
curl -s -X POST "http://localhost:8000/ingest/satellite-frame?satellite_name=GOES&region=NorthAmerica&band=VIS&timestamp=2026-04-17T10:35:00Z&width=1024&height=1024" | python -m json.tool
echo ""

# Final system info
echo "8. Final System Information:"
curl -s http://localhost:8000/info | python -m json.tool
echo ""

echo "=== Test Suite Complete ==="
